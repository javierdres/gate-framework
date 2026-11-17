---
seed_id: SEED-BACK-16
kind: baseline
lesson: The escape function of a document generator covered one reserved character of its format; a name with any other broke legal documents or cut their text, in dozens of fixes across two products.
title: Every value entering a document template is fully escaped
severity: hard
scope: [backend]
projects: [cross-cutting]
tags: [documents, business-defect]
verification: manual
detected_by: review
applies_when: [documents != none]
---

# SEED-BACK-16 · Every value entering a document template is fully escaped

## Do not

Insert data into a document template (HTML, LaTeX, DOCX, PDF) without escaping it, or with an
escape that covers only some reserved characters.

## Do instead

Every value passes through one escape function that covers all the reserved characters of the
format. Only the template's fixed text carries format commands. Each type of legal document has
a sample approved by product.

## Why

A legal document issued wrong is a business defect, and the inputs that break it are the rare
names nobody tests.

## How it is checked

In review, every value inserted in a template goes through the escape function. A test with every
reserved character of the format.

## Exceptions

None. This is a hard rule.
