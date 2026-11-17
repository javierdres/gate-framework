#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Decisions and reasons of the permissions guard.

    python3 tools/guards/tests/test_permissions.py

A guard that asks whenever it fails hides its own bugs behind a plausible answer, so these tests
check the reason as well as the decision. Run them after every change to the guard.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GUARD = os.path.join(os.path.dirname(HERE), "permissions.py")


def sh(args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


class Guard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.grants = os.path.join(cls.tmp, "grants")
        cls.repo = os.path.join(cls.tmp, "repo")
        os.makedirs(cls.repo)
        sh(["git", "init", "-q", "-b", "main"], cls.repo)
        cls.remote = os.path.join(cls.tmp, "remote.git")
        sh(["git", "init", "-q", "--bare", cls.remote], cls.tmp)
        sh(["git", "remote", "add", "origin", cls.remote], cls.repo)
        sh(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "x"], cls.repo)
        sh(["git", "checkout", "-q", "-b", "feature/x"], cls.repo)
        cls.repo = os.path.realpath(cls.repo)

    def run_guard(self, payload, fmt="json", raw=None):
        env = dict(os.environ, SDLC_GRANTS_DIR=self.grants)
        data = raw if raw is not None else json.dumps(payload)
        args = [sys.executable, GUARD, "check"] + (["--format", fmt] if fmt else [])
        p = subprocess.run(args, input=data, capture_output=True, text=True, env=env)
        out = json.loads(p.stdout) if p.stdout.strip().startswith("{") else None
        return p.returncode, out, p.stderr

    def bash(self, command, session="s1"):
        return {"tool_name": "Bash", "tool_input": {"command": command},
                "session_id": session, "cwd": self.repo}

    def grant(self, session, kind, value):
        env = dict(os.environ, SDLC_GRANTS_DIR=self.grants)
        subprocess.run([sys.executable, GUARD, "grant", session, kind, value],
                       capture_output=True, text=True, env=env, check=True)

    def decision(self, command, session="s1"):
        _, out, _ = self.run_guard(self.bash(command, session))
        return (out or {}).get("decision"), (out or {}).get("reason", "")

    # local work passes untouched
    def test_local_commands_pass(self):
        for c in ("ls -la", "git status", "git stash push", "git commit -m x", "python3 -m pytest",
                  "gh api repos/a/b", "curl https://example.com"):
            self.assertEqual(self.decision(c), (None, ""), c)

    # outward writes ask until the scope is granted
    def test_push_asks_then_passes_after_grant(self):
        d, r = self.decision("git push origin feature/x", "s-push")
        self.assertEqual(d, "ask")
        self.assertIn("grant s-push repo", r)
        self.grant("s-push", "repo", self.repo)
        self.assertEqual(self.decision("git push origin feature/x", "s-push")[0], "allow")
        self.assertEqual(self.decision("git push -u origin HEAD", "s-push")[0], "allow")

    def test_change_request_and_api_writes_are_watched(self):
        for c in ("gh pr create --fill", "glab mr create", "gh api repos/a/b/issues -f title=x",
                  "gh api -X POST repos/a/b/issues", "glab api --method PUT projects/1"):
            self.assertEqual(self.decision(c, "s-none")[0], "ask", c)

    # never delegated, whatever was granted
    def test_never_delegated_even_with_grant(self):
        self.grant("s-all", "repo", self.repo)
        never = {
            "git push origin main": "default branch",
            "git push origin HEAD:main": "default branch",
            "git push origin feature/x:refs/heads/main": "default branch",
            "git push --force origin feature/x": "forced",
            "git push -f origin feature/x": "forced",
            "git push origin +feature/x": "forced",
            "git push --force-with-lease": "forced",
            "git push --mirror origin": "mirrored",
            "git push --prune origin": "pruning",
            "git push origin :old": "deleting",
            "git push --delete origin old": "deleting",
            "git push --all origin": "every branch",
            "gh pr merge 3": "merge",
            "glab mr merge 3": "merge",
            "gh api -X DELETE repos/a/b": "deletion",
            "terraform apply": "infrastructure",
            "kubectl delete pod x": "infrastructure",
            "python3 tools/guards/permissions.py grant s1 repo .": "authorisation",
        }
        for command, why in never.items():
            d, r = self.decision(command, "s-all")
            self.assertEqual(d, "ask", command)
            self.assertIn(why, r, command)

    def test_bypasses_found_in_review_all_ask(self):
        """Every way the second simulation found to slip a write past the guard."""
        self.grant("s-by", "repo", self.repo)
        other = tempfile.mkdtemp()
        sh(["git", "init", "-q"], other)
        bypasses = [
            "sh -c 'git push origin feature/x'",
            "bash -c \"git push origin main\"",
            "(git push origin main)",
            "echo $(git push origin main)",
            "echo `git push origin feature/x`",
            "eval git push origin feature/x",
            "/usr/bin/git push origin main",
            "cd %s && git push origin x" % other,
            "git push https://example.com/other/repo.git feature/x",
            "python3 \"tools/guards/permissions.py\" 'grant' s-by repo /tmp",
            "python3 tools/guards/perm''issions.py grant s-by repo /tmp",
            "echo '{\"repo\": [\"/\"]}' > personal/grants/s-by.json",
            "gh api -X delete repos/a/b",
            "env GIT_TRACE=1 git push origin feature/x",
        ]
        for command in bypasses:
            d, r = self.decision(command, "s-by")
            self.assertEqual(d, "ask", command)
            self.assertIn("Always asks", r, command)

    def test_infrastructure_reads_pass_and_everything_else_asks(self):
        self.grant("s-infra", "repo", self.repo)
        for c in ("kubectl get pods -n prod", "kubectl -n prod logs deploy/api --tail 50",
                  "kubectl --context prod describe pod x", "kubectl auth can-i get pods",
                  "helm list -A", "helm status api -n prod", "terraform validate",
                  "kubectl get pods | grep api", "cat terraform/main.tf", "ls helm-charts/",
                  "grep -rn kubectl.apply docs/"):
            self.assertEqual(self.decision(c, "s-infra"), (None, ""), c)
        asks = {
            "kubectl apply -f x.yaml": "infrastructure",
            "kubectl -n prod delete pod x": "infrastructure",
            "kubectl exec -it x -- sh": "infrastructure",
            "kubectl config use-context prod": "infrastructure",
            "kubectl get pods && kubectl delete pod x": "infrastructure",
            "kubectl get pods -o yaml | kubectl apply -f -": "infrastructure",
            "sh -c 'kubectl delete pod x'": "infrastructure",
            "echo $(kubectl scale deploy x --replicas 0)": "infrastructure",
            "nice kubectl rollout restart deploy/x": "infrastructure",
            "KUBECONFIG=/x kubectl drain node": "infrastructure",
            "helm upgrade api ./chart": "infrastructure",
            "terraform apply": "infrastructure",
            "terraform plan": "infrastructure",
            "kubectl get secret db -o yaml": "credentials",
            "kubectl -n prod describe secrets": "credentials",
        }
        for command, why in asks.items():
            d, r = self.decision(command, "s-infra")
            self.assertEqual(d, "ask", command)
            self.assertIn(why, r, command)

    def test_api_clients_read_freely_and_writes_ask(self):
        self.grant("s-cli", "repo", self.repo)
        for c in ("tools/clients/tracker.sh GET issue/ABC-1", "python3 tools/clients/obs.py HEAD /health",
                  "./tools/clients/tracker.sh GET search | jq ."):
            self.assertEqual(self.decision(c, "s-cli"), (None, ""), c)
        for c in ("tools/clients/tracker.sh POST issue/ABC-1/comment body.json",
                  "tools/clients/tracker.sh issue/ABC-1", "python3 tools/clients/obs.py put /x",
                  "git status && tools/clients/tracker.sh DELETE issue/ABC-1",
                  "sh -c 'tools/clients/tracker.sh POST x'"):
            d, r = self.decision(c, "s-cli")
            self.assertEqual(d, "ask", c)

    def test_linear_writes_can_be_authorised(self):
        save = {"tool_name": "mcp__linear__save_issue", "tool_input": {"teamKey": "LIN", "title": "x"},
                "session_id": "s-lin", "cwd": self.repo}
        comment = {"tool_name": "mcp__linear__create_comment", "tool_input": {"issueId": "LIN-42", "body": "x"},
                   "session_id": "s-lin", "cwd": self.repo}
        self.assertEqual(self.run_guard(save)[1]["decision"], "ask")
        self.assertIn("grant s-lin tracker LIN", self.run_guard(comment)[1]["reason"])
        self.grant("s-lin", "tracker", "LIN")
        self.assertEqual(self.run_guard(save)[1]["decision"], "allow")
        self.assertEqual(self.run_guard(comment)[1]["decision"], "allow")

    def test_graphql_clients_read_by_intent(self):
        self.assertEqual(self.decision("tools/clients/linear.sh QUERY issues.graphql", "s-gql"), (None, ""))
        d, r = self.decision("tools/clients/linear.sh MUTATION comment.graphql LIN-42", "s-gql")
        self.assertEqual(d, "ask")
        self.assertIn("tracker LIN", r)
        self.grant("s-gql", "tracker", "LIN")
        self.assertEqual(self.decision("tools/clients/linear.sh MUTATION comment.graphql LIN-42", "s-gql")[0], "allow")
        self.assertEqual(self.decision("tools/clients/obs.sh MUTATION x", "s-gql")[0], "ask")

    def test_reads_are_not_slowed_down(self):
        for c in ("gh api user | python3 -c 'import json,sys; print(1)'", "glab api projects/1",
                  "git log --oneline | head", "cd /tmp && ls", "curl -s https://example.com | jq ."):
            self.assertEqual(self.decision(c), (None, ""), c)

    def test_file_tools_cannot_write_the_grants(self):
        ev = {"tool_name": "Write", "tool_input": {"file_path": "/x/sdlc/personal/grants/s1.json"}, "session_id": "s1"}
        out = self.run_guard(ev)[1]
        self.assertEqual(out["decision"], "ask")
        ev["tool_input"] = {"file_path": "/x/sdlc/README.md"}
        self.assertIsNone(self.run_guard(ev)[1])

    def test_connectors(self):
        cases = {
            "mcp__gitlab__merge_merge_request": ("ask", "merge or deletion"),
            "mcp__github__create_pull_request": ("ask", "connector"),
            "mcp__atlassian__executeWrite": ("ask", "connector"),
            "mcp__atlassian__executeDestructive": ("ask", "merge or deletion"),
            "mcp__atlassian__executeRead": (None, None),
            "mcp__atlassian__getJiraIssue": (None, None),
            "mcp__atlassian__searchJiraIssuesUsingJql": (None, None),
            "mcp__atlassian__discover": (None, None),
            "mcp__linear__list_issues": (None, None),
            "mcp__linear__save_issue": ("ask", "tracker"),
            "mcp__someservice__frobnicate": ("ask", "does not recognise"),
        }
        for name, (decision, why) in cases.items():
            out = self.run_guard({"tool_name": name, "tool_input": {}, "session_id": "s-c"})[1]
            if decision is None:
                self.assertIsNone(out, name)
            else:
                self.assertEqual(out["decision"], decision, name)
                self.assertIn(why, out["reason"], name)

    def test_bare_push_on_default_branch_always_asks(self):
        sh(["git", "checkout", "-q", "main"], self.repo)
        try:
            self.grant("s-main", "repo", self.repo)
            d, r = self.decision("git push", "s-main")
            self.assertEqual(d, "ask")
            self.assertIn("default branch", r)
        finally:
            sh(["git", "checkout", "-q", "feature/x"], self.repo)

    # every segment of a chain is judged
    def test_every_segment_of_a_chain_is_judged(self):
        self.grant("s-chain", "repo", self.repo)
        other = tempfile.mkdtemp()
        sh(["git", "init", "-q"], other)
        mixed = "git -C %s push origin x && git push origin feature/x" % other
        self.assertEqual(self.decision(mixed, "s-chain")[0], "ask")
        self.assertEqual(self.decision("git push origin feature/x && gh pr merge 1", "s-chain")[0], "ask")
        self.assertEqual(self.decision("git commit -m x; git push origin feature/x", "s-chain")[0], "allow")

    # tracker writes
    def test_tracker(self):
        ev = {"tool_name": "mcp__tracker__createIssue", "tool_input": {"projectKey": "ABC"}, "session_id": "s-t"}
        self.assertEqual(self.run_guard(ev)[1]["decision"], "ask")
        self.grant("s-t", "tracker", "abc")
        self.assertEqual(self.run_guard(ev)[1]["decision"], "allow")
        ev["tool_input"] = {"issueIdOrKey": "ABC-3"}
        ev["tool_name"] = "mcp__tracker__deleteIssue"
        out = self.run_guard(ev)[1]
        self.assertEqual(out["decision"], "ask")
        self.assertIn("deletion", out["reason"])
        read = {"tool_name": "mcp__tracker__getIssue", "tool_input": {"issueIdOrKey": "ABC-3"}, "session_id": "s-t"}
        self.assertEqual(self.run_guard(read)[0], 0)
        self.assertIsNone(self.run_guard(read)[1])

    # it never fails open
    def test_never_fails_open(self):
        code, out, _ = self.run_guard(None, raw="not json")
        self.assertEqual(out["decision"], "ask")
        code, out, _ = self.run_guard(None, raw="")
        self.assertEqual(out["decision"], "ask")
        code, out, _ = self.run_guard(None, raw="[]")
        self.assertEqual(out["decision"], "ask")
        code, out, err = self.run_guard(self.bash("git push origin feature/x", "s-x"), fmt="")
        self.assertEqual(code, 2)
        env = dict(os.environ, SDLC_GRANTS_DIR=self.grants)
        p = subprocess.run([sys.executable, GUARD, "check", "--format"], input="{}",
                           capture_output=True, text=True, env=env)
        self.assertEqual(p.returncode, 2, "a --format without value must still block, never pass")

    def test_claude_format(self):
        _, out, _ = self.run_guard(self.bash("gh pr merge 1"), fmt="claude")
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask")


REMINDER = os.path.join(os.path.dirname(HERE), "log_reminder.py")


class Ported(unittest.TestCase):
    """Autonomous mode, approvals, passes, other assistants' tool names, the home folder and
    repositories named by their platform path."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.grants = os.path.join(self.tmp, "grants")
        self.config = os.path.join(self.tmp, "sdlc.yml")
        self.repo = os.path.realpath(os.path.join(self.tmp, "repo-a"))
        os.makedirs(self.repo)
        sh(["git", "init", "-q", "-b", "main"], self.repo)
        sh(["git", "remote", "add", "origin", "git@code.example.com:grp/sub/repo-a.git"], self.repo)
        sh(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "x"], self.repo)
        sh(["git", "checkout", "-q", "-b", "feature/x"], self.repo)
        self.env = dict(os.environ, SDLC_GRANTS_DIR=self.grants, SDLC_CONFIG=self.config)

    def allow_autonomous(self, value):
        with open(self.config, "w") as f:
            f.write("system:\n  name: x\npermissions:\n  autonomous_allowed: %s   # opt-in\n" % value)

    def cli(self, *args, env=None):
        return subprocess.run([sys.executable, GUARD] + list(args), capture_output=True, text=True,
                              env=env or self.env)

    def guard(self, event, fmt="json"):
        p = subprocess.run([sys.executable, GUARD, "check", "--format", fmt], input=json.dumps(event),
                           capture_output=True, text=True, env=self.env)
        out = json.loads(p.stdout) if p.stdout.strip().startswith("{") else None
        return p.returncode, out, p.stdout + p.stderr

    def bash(self, command, session="s", cwd=None):
        return {"tool_name": "Bash", "tool_input": {"command": command}, "session_id": session,
                "cwd": cwd or self.repo}

    def decision(self, event):
        out = self.guard(event)[1]
        return (out or {}).get("decision"), (out or {}).get("reason", "")

    # (a) autonomous mode is the organisation's opt-in, and never covers the grants
    def test_autonomous_needs_the_opt_in(self):
        p = self.cli("grant", "s", "autonomous")
        self.assertEqual(p.returncode, 1)
        self.assertIn("not enabled", p.stdout)
        self.allow_autonomous("false")
        self.assertEqual(self.cli("grant", "s", "autonomous").returncode, 1)
        self.allow_autonomous("true")
        self.assertEqual(self.cli("grant", "s", "autonomous").returncode, 0)
        for c in ("gh pr merge 1", "git push origin main", "terraform apply", "git push origin feature/x"):
            self.assertEqual(self.decision(self.bash(c)), (None, ""), c)
        for c in ("python3 tools/guards/permissions.py grant s repo .", "python3 tools/guards/permissions.py revoke s",
                  "echo 1 > personal/grants/s.pass", "python3 tools/guards/log_reminder.py --passes"):
            self.assertEqual(self.decision(self.bash(c))[0], "ask", c)
        write = {"tool_name": "Write", "tool_input": {"file_path": os.path.join(self.grants, "s.json")}, "session_id": "s"}
        self.assertEqual(self.decision(write)[0], "ask")
        self.assertIn("autonomous mode: active", self.cli("show", "s").stdout)
        # withdrawn by the organisation, a recorded grant stops counting
        self.allow_autonomous("false")
        self.assertEqual(self.decision(self.bash("gh pr merge 1"))[0], "ask")
        self.assertIn("no longer allows", self.cli("show", "s").stdout)
        self.allow_autonomous("true")
        self.cli("revoke", "s", "autonomous")
        self.assertEqual(self.decision(self.bash("gh pr merge 1"))[0], "ask")

    def test_granting_autonomous_always_asks(self):
        self.allow_autonomous("true")
        d, r = self.decision(self.bash("python3 tools/guards/permissions.py grant s autonomous"))
        self.assertEqual(d, "ask")
        self.assertIn("Always asks", r)

    # (b) an approval is a person's, never the assistant's
    def test_approvals_always_ask(self):
        self.cli("grant", "s", "repo", self.repo)
        for c in ("gh pr review 3 --approve", "gh pr review 3 -a", "glab mr approve 3", "glab mr revoke 3",
                  "gh api -X POST repos/grp/repo-a/pulls/3/reviews -f event=APPROVE",
                  "glab api -X POST projects/grp%2Fsub%2Frepo-a/merge_requests/3/approve",
                  "curl -X POST https://code.example.com/api/v4/projects/1/merge_requests/3/approve"):
            d, r = self.decision(self.bash(c))
            self.assertEqual(d, "ask", c)
            self.assertIn("approval", r, c)
        out = self.guard({"tool_name": "mcp__github__approve_pull_request", "tool_input": {}, "session_id": "s"})[1]
        self.assertIn("approval", out["reason"])
        self.assertEqual(self.decision(self.bash("gh pr review 3 --comment -b x"))[0], "allow")

    # (c) assistants that can only block: one OK, one action
    def reminder(self, prompt, session="s"):
        p = subprocess.run([sys.executable, REMINDER, "--passes"], capture_output=True, text=True, env=self.env,
                           input=json.dumps({"session_id": session, "prompt": prompt}))
        self.assertIn("Log:", p.stdout)
        return os.path.exists(os.path.join(self.grants, session + ".pass"))

    def test_a_pass_covers_one_action(self):
        code, _, err = self.guard(self.bash("git push origin feature/x"), fmt="exit")
        self.assertEqual(code, 2)
        self.assertIn('reply "ok"', err)
        for prompt in ("si quieres, revisa primero", "yes but first explain", "nope", "ok " + "x" * 90):
            self.assertFalse(self.reminder(prompt), prompt)
        for prompt in ("ok", "OK, go", "Dale", "sí", "yes!", "go ahead please"):
            self.assertTrue(self.reminder(prompt), prompt)
        code, _, out = self.guard(self.bash("git push origin feature/x"), fmt="exit")
        self.assertEqual(code, 0)
        self.assertIn("OK was used", out)
        self.assertEqual(self.guard(self.bash("git push origin feature/x"), fmt="exit")[0], 2)
        # the pass only works in exit format; elsewhere the assistant asks on screen
        self.reminder("ok")
        self.assertEqual(self.decision(self.bash("git push origin feature/x"))[0], "ask")

    def test_a_pass_never_touches_the_grants_but_covers_a_grant(self):
        self.reminder("ok")
        write = {"tool_name": "fs_write", "tool_input": {"path": os.path.join(self.grants, "s.json")}, "session_id": "s"}
        code, _, err = self.guard(write, fmt="exit")
        self.assertEqual(code, 2)
        self.assertIn("Only the person", err)
        code, _, err = self.guard(self.bash("python3 tools/guards/log_reminder.py --passes"), fmt="exit")
        self.assertEqual(code, 2)
        self.assertIn("Only the person", err)
        self.assertTrue(os.path.exists(os.path.join(self.grants, "s.pass")), "a refused action spends nothing")
        code, _, _ = self.guard(self.bash("python3 tools/guards/permissions.py grant s repo ."), fmt="exit")
        self.assertEqual(code, 0, "the person's OK to an authorisation covers the command")

    def test_a_stale_pass_is_dropped(self):
        os.makedirs(self.grants, exist_ok=True)
        with open(os.path.join(self.grants, "s.pass"), "w") as f:
            f.write("%d\n" % (time.time() - 16 * 60))
        self.assertEqual(self.guard(self.bash("git push origin feature/x"), fmt="exit")[0], 2)
        self.assertFalse(os.path.exists(os.path.join(self.grants, "s.pass")))

    # (d) other assistants' tool names
    def test_other_assistants_tool_names(self):
        cases = [
            ({"tool_name": "execute_bash", "tool_input": {"command": "gh pr merge 1"}}, "ask", "merge"),
            ({"tool_name": "run_shell_command", "tool_input": json.dumps({"command": "git push origin main"})},
             "ask", "default branch"),
            ({"tool_name": "shell", "tool_input": {"cmd": "glab mr merge 1"}}, "ask", "merge"),
            ({"tool_name": "fs_write", "tool_input": {"path": "/x/personal/grants/s.json"}}, "ask", "authorisations"),
            ({"tool_name": "str_replace", "tool_input": {"path": "/x/README.md"}}, None, None),
            ({"tool_name": "github___merge_pull_request", "tool_input": {}}, "ask", "merge"),
            ({"tool_name": "@linear/save_issue", "tool_input": {"teamKey": "LIN"}}, "ask", "tracker LIN"),
            ({"tool_name": "linear/list_issues", "tool_input": {}}, None, None),
            ({"tool_name": "mcp_linear_list_issues", "tool_input": {}}, None, None),
            ({"tool_name": "mcp_github_create_pull_request", "tool_input": {}}, "ask", "connector"),
        ]
        for event, decision, why in cases:
            event = dict(event, session_id="s", cwd=self.repo)
            d, r = self.decision(event)
            self.assertEqual(d, decision, event["tool_name"])
            if why:
                self.assertIn(why, r, event["tool_name"])

    # (e) the home folder is never a repository to authorise
    def test_home_folder_is_never_authorised(self):
        home = os.path.realpath(os.path.join(self.tmp, "home"))
        os.makedirs(home)
        sh(["git", "init", "-q"], home)
        p = self.cli("grant", "s", "repo", home, env=dict(self.env, HOME=home))
        self.assertEqual(p.returncode, 1)
        self.assertIn("home folder", p.stdout)
        os.makedirs(self.grants, exist_ok=True)
        with open(os.path.join(self.grants, "s.json"), "w") as f:
            json.dump({"repo": [home]}, f)
        p = subprocess.run([sys.executable, GUARD, "check", "--format", "json"], capture_output=True, text=True,
                           input=json.dumps(self.bash("git push origin x", cwd=home)), env=dict(self.env, HOME=home))
        self.assertEqual(json.loads(p.stdout)["decision"], "ask")

    # (f) a repository named by its platform path matches the authorised clone
    def test_platform_path_matches_the_authorised_clone(self):
        sys.path.insert(0, os.path.dirname(HERE))
        import permissions
        for url, path in (("git@code.example.com:grp/sub/name.git", "grp/sub/name"),
                          ("https://code.example.com/grp/sub/name", "grp/sub/name"),
                          ("https://code.example.com/grp/name.git/", "grp/name"),
                          ("ssh://git@code.example.com:2222/grp/name.git", "grp/name"), ("", "")):
            self.assertEqual(permissions.platform_path(url), path, url)
        elsewhere = tempfile.mkdtemp()
        allowed = ("glab mr create --repo grp/sub/repo-a --fill", "glab mr create -R grp/sub/repo-a",
                   "glab api -X POST projects/grp%2Fsub%2Frepo-a/merge_requests -f title=x",
                   "gh pr create --repo=grp/sub/repo-a")
        for c in allowed:
            self.assertEqual(self.decision(self.bash(c, cwd=elsewhere))[0], "ask", c)
        self.cli("grant", "s", "repo", self.repo)
        self.assertIn('"grp/sub/repo-a"', self.cli("show", "s").stdout)
        for c in allowed:
            self.assertEqual(self.decision(self.bash(c, cwd=elsewhere))[0], "allow", c)
        for c in ("glab mr create -R grp/other", "gh api -X POST repos/grp/other/pulls -f x=1",
                  "glab api -X PUT projects/grp%2Fsub%2Frepo-a/merge_requests/1/merge",
                  "glab api -X DELETE projects/grp%2Fsub%2Frepo-a"):
            self.assertEqual(self.decision(self.bash(c, cwd=elsewhere))[0], "ask", c)
        self.cli("revoke", "s", "repo", self.repo)
        self.assertNotIn("repo-a", self.cli("show", "s").stdout)


if __name__ == "__main__":
    unittest.main(verbosity=1)
