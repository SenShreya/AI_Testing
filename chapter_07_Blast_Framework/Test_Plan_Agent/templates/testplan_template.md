# Test Plan
### `<Project Name>`

| | |
|---|---|
| **Document ID** | TEST PLAN-v0.1 |
| **Version Number** | 0.1 |
| **Issue Date** | April 01, 2020 |
| **Classification** | Public |

---

## Copyright Notice

© COMPANYNAME, (original issue year – current issue year)
All Rights Reserved

The information contained in this document is the property of COMPANYNAME. No part of this document may be reproduced, stored in a retrieval system, or transmitted in any form, or by any means; mechanical, photocopying, recording, or otherwise, without the prior written consent of COMPANYNAME. Under the law, copying includes translating into another language or format. Legal action will be taken against any infringement.

The information contained in this document is subject to change without notice and does not carry any contractual obligation for COMPANYNAME. COMPANYNAME reserves the right to make changes to any products or services described in this document at any time without notice. COMPANYNAME shall not be held responsible for the direct or indirect consequences of the use of the information contained in this document.

---

## Revision History

| **Date** | **Version** | **Description** | **Author(s)** |
|---|---|---|---|
| 04/01/2020 | 0.1 | Draft Version | John Doe |
| | | | |
| | | | |

---

## Sign Off

The reviewer signoff shall signify the recommendation for acceptance of this document.

**Reviewed By (Customer)**

| **Reviewed By (Customer)** | **Signature** | **Date** |
|---|---|---|
| | | |
| | | |
| | | |

**Prepared By / Acknowledged By**

| **Prepared By** | **Acknowledged By** |
|---|---|
| `<Name>` | `<Name>` |
| Title: `<Position>` | Title: `<Position>` |
| COMPANYNAME | COMPANYNAME |
| Date: | Date: |

**Accepted By**

| **Accepted By** | **Accepted By** |
|---|---|
| `<Name>` | `<Name>` |
| Title: `<Position>` | Title: `<Position>` |
| `<Customer Company Name>` | `<Customer Company Name>` |
| Date: | Date: |

---

## Table of Contents

- [List of Tables](#list-of-tables)
- [List of Figures](#list-of-figures)
- [1. Introduction](#1-introduction)
  - [1.1 Overview of the System](#11-overview-of-the-system)
  - [1.2 Purpose](#12-purpose)
  - [1.3 Acronyms and Abbreviations](#13-acronyms-and-abbreviations)
- [2. Test Level](#2-test-level)
  - [2.1 Test Level – Entry and Exit](#21-test-level--entry-and-exit)
  - [2.2 Test Levels and Test Items](#22-test-levels-and-test-items)
  - [2.3 Exclusions](#23-exclusions)
  - [2.4 Test Criteria](#24-test-criteria)
    - [2.4.1 Item Pass / Fail Criteria](#241-item-pass--fail-criteria)
    - [2.4.2 Suspension and Resumption Criteria](#242-suspension-and-resumption-criteria)
    - [2.4.3 Regression / Verification Criteria](#243-regression--verification-criteria)
  - [2.5 Constraints and Deficiencies](#25-constraints-and-deficiencies)
- [3. Test Reporting and Defect Tracking](#3-test-reporting-and-defect-tracking)
- [4. Change Management](#4-change-management)
- [5. Test Planning](#5-test-planning)
  - [5.1 Roles and Responsibilities](#51-roles-and-responsibilities)
  - [5.2 Test Schedule](#52-test-schedule)
  - [5.3 Environment Needs](#53-environment-needs)
    - [5.3.1 Hardware](#531-hardware)
    - [5.3.2 Software](#532-software)
  - [5.4 Training Needs](#54-training-needs)
  - [5.5 Risk and Contingencies](#55-risk-and-contingencies)
- [6. Customer Validation Plan](#6-customer-validation-plan)
  - [6.1 Roles and Responsibilities](#61-roles-and-responsibilities)
  - [6.2 Validation Schedule](#62-validation-schedule)
  - [6.3 Validation Environment Needs](#63-validation-environment-needs)
    - [6.3.1 Hardware](#631-hardware)
    - [6.3.2 Software](#632-software)
  - [6.4 Validation Items](#64-validation-items)
  - [6.5 Reporting and Tracking to Closure](#65-reporting-and-tracking-to-closure)
- [Appendix](#appendix)

---

## List of Tables

1. Table 1: Test Level – Entry and Exit
2. Table 2: Test Levels and Test Items
3. Table 3: Roles and Responsibilities
4. Table 4: Test Schedule
5. Table 5: Hardware Details
6. Table 6: Software Details
7. Table 7: Training Needs
8. Table 8: Risk and Contingencies
9. Table 9: Customer Roles and Responsibilities
10. Table 10: Validation Schedule
11. Table 11: Validation Hardware Details
12. Table 12: Validation Software Details

## List of Figures

*(None)*

---

## 1. Introduction

### 1.1 Overview of the System

`<Describe the overview of the application>`

### 1.2 Purpose

`<The purpose of this Test Plan is to clearly describe the various testing techniques and testing approaches followed for testing the system>`

### 1.3 Acronyms and Abbreviations

`<This subsection provides the definitions of all terms, acronyms and abbreviations required to properly interpret the Test Plan document>`

---

## 2. Test Level

`<Mention the applicable levels of testing – Unit, integration, system, acceptance and final acceptance. Describe a short description on how they are to be administered and if a few are not applicable state why they are not available>`

### 2.1 Test Level – Entry and Exit

*Table 1: Test Level – Entry and Exit*

| Entry Level | **Test Level** | **Exit Level** |
|---|---|---|
| 1. Functional Spec reviewed and available.<br>2. System Test Cases reviewed and ready. | System Testing | System test cases 100% executed.<br>No severity 'Fatal' or 'High' problem outstanding.<br>Test results documented in TPR. |
| | | |

### 2.2 Test Levels and Test Items

*Table 2: Test Levels and Test Items*

| Test Level | **Test Items (Test Procedure, Test Cases, Scripts Reference)** | **Tools Used (if any)** | **Coverage** |
|---|---|---|---|
| System Testing | System Test cases | Manual | As per the Requirement Specification |

### 2.3 Exclusions

`<No exclusions. The entire functionality as defined in the Requirement Specifications document shall be tested>`

### 2.4 Test Criteria

#### 2.4.1 Item Pass / Fail Criteria

`<When the Expected Result matches with the Actual Result the corresponding Test Case is marked as 'Pass'. Otherwise, the Test Case is marked as 'Fail'. Test Problem Report (TPR) for failed test cases will be raised with a brief description of steps that actually lead to the issue. The Test Case ID is marked in the TPR against the Issue Description for better understanding. All issues in TPR shall be tracked to closure.>`

#### 2.4.2 Suspension and Resumption Criteria

`<When 40% of executed test cases fail then testing would be suspended & the application would be returned to the development team for rework. Also testing would be suspended when the basic functionality is not met.`

`Testing would be resumed when the raised issues are fixed by the development team.>`

#### 2.4.3 Regression / Verification Criteria

`<If the failed test cases percentage is more than 40% then regression testing would be performed, else it undergoes a verification cycle.>`

### 2.5 Constraints and Deficiencies

`<Inadequate time for Testing, Testing environment not available in time, Tester not familiar with the system, Delay in Receiving baseline documents, Delay in receiving the fixes from Development Team, Poor System Performance/response>`

---

## 3. Test Reporting and Defect Tracking

`<All defects raised during testing would be logged in an excel sheet>`

---

## 4. Change Management

`<Changes happen in the form of a requirement change or design change. Test plan and other test artifacts are analyzed for the impact due to change. Changes are then appropriately carried out and go through the same workflow as preparation, review, verification and baseline. Traceability matrix is revisited to accommodate the changes>`

---

## 5. Test Planning

### 5.1 Roles and Responsibilities

*Table 3: Roles and Responsibilities*

| Role | **Responsibility** | **Person** |
|---|---|---|
| Test Lead | Preparation of Test plan, Review of Test Cases, Testing, Test Monitoring and Test Consolidation and Analysis | |
| Tester | Preparation of Test Cases, Testing, Defect Reporting | |

### 5.2 Test Schedule

*Table 4: Test Schedule*

| Task | **Start Date** | **End Date** | **Resource** | **Deliverable** |
|---|---|---|---|---|
| Test case Preparation | `<dd Month yyyy>` | `<dd Month yyyy>` | `<Name>` | Test cases |
| Testing | `<dd Month yyyy>` | `<dd Month yyyy>` | `<Name>` | Test Problem Report, Test Summary Report |

`<The above could be linked to the overall Project Schedule>`

### 5.3 Environment Needs

#### 5.3.1 Hardware

*Table 5: Hardware Details*

| S. No | **Testing Task** | **Hardware Details** | **Needed on or Before** |
|---|---|---|---|
| | | | |
| | | | |

#### 5.3.2 Software

*Table 6: Software Details*

| S. No | **Testing Task** | **Software Details** | **Needed on or Before** |
|---|---|---|---|
| | | | |
| | | | |

### 5.4 Training Needs

`<Give the training details to the Testing team. Could be specific to domain, technology and test tools>`

*Table 7: Training Needs*

| S. No | **Training Description** | **Needed on or Before** |
|---|---|---|
| | | |
| | | |
| | | |

### 5.5 Risk and Contingencies

*Table 8: Risk and Contingencies*

| S. No | **Risk** | **Mitigation** | **Contingency** |
|---|---|---|---|
| | | | |
| | | | |

---

## 6. Customer Validation Plan

`<Mention the steps taken for validating at the customer end. This would be UAT, FAT or intermediate testing or parallel testing. This section needs to indicate the various types of validations planned, validating components and the schedule>`

### 6.1 Roles and Responsibilities

`<State the various roles and their responsibilities here in this section. This could be in overall sync with the PMP roles and responsibilities>`

*Table 9: Customer Roles and Responsibilities*

| Role (Customer end and COMPANYNAME) | **Responsibility** | **Person** |
|---|---|---|
| | | |
| | | |
| | | |

### 6.2 Validation Schedule

`<Give the complete validation schedule and this has to be part of the overall project schedule>`

*Table 10: Validation Schedule*

| Validation Item | **Start Date** | **End Date** | **Entry Criteria** | **Exit Criteria** |
|---|---|---|---|---|
| `<Build or Prototype or Component inclusive of iteration>` | | | | |
| | | | | |
| | | | | |
| | | | | |

\* The above could be linked to the overall Project schedule

### 6.3 Validation Environment Needs

`<Give the testing hardware/software environmental details here. This is inclusive of all test levels, techniques and in terms of hardware and software. Also mention the location where the validation would be done>`

#### 6.3.1 Hardware

*Table 11: Validation Hardware Details*

| S. No | **Hardware Details** | **Needed on or Before** |
|---|---|---|
| | | |
| | | |
| | | |

#### 6.3.2 Software

*Table 12: Validation Software Details*

| S. No | **Software Details** | **Needed on or Before** |
|---|---|---|
| | | |
| | | |
| | | |

### 6.4 Validation Items

`<Mention what are the items that have to be used for validation. These would be scenarios or scenario test cases or some cases written and given by customer. Mention what would be the validation items customer would use>`

### 6.5 Reporting and Tracking to Closure

`<Mention how customer validation results would be reported – either in TPR or customer-given format and also mention how they will be tracked to closure>`

---

## Appendix