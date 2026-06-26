# Trade Thesis Specification

> **Version:** 1.0 (Living Document)

---

# Purpose

The Trade Thesis Specification defines how every trading idea is represented, monitored, and evaluated inside TradePilotAI.

TradePilotAI is **not** a stock scanner.

TradePilotAI is a **Trade Thesis Operating System**.

The objective is to continuously monitor a trading thesis from the moment it is created until it is either completed or invalidated.

This document serves as the foundation for every future component of TradePilotAI, including:

* Scanner
* Notifications
* AI Reasoning Engine
* Event Monitoring
* Knowledge Graph
* Trade Journal
* Historical Analysis

---

# Core Philosophy

TradePilotAI does **not** monitor stocks.

TradePilotAI monitors **trade theses**.

A ticker is simply one attribute of a trade thesis.

The same ticker may have multiple independent theses.

Example:

AAOI

* Thesis A

  * Swing Trade
  * Buy Zone: 156-162

* Thesis B

  * Income Strategy
  * Different monitoring rules

Each thesis is treated independently.

---

# What is a Trade Thesis?

A Trade Thesis represents the reasoning behind a potential trade.

It is **not** simply:

> Buy Stock XYZ

Instead it captures:

> "I believe this security presents a high-probability opportunity because specific technical, structural, or fundamental conditions exist."

---

# Components of a Trade Thesis

Every thesis should contain, at minimum:

* Ticker
* Buy Zone
* Stop Loss
* Target (optional)
* Time Horizon
* Setup Type
* User Reasoning
* User Conviction Score
* Notes

Future versions may include:

* AI Thesis
* AI Conviction Score
* Historical Performance
* Related Events
* Supporting Evidence

---

# Trade Lifecycle

Every thesis progresses through a lifecycle.

Initial proposal:

WATCH

↓

BUY ZONE

↓

DECISION ZONE

↓

INVALIDATED

Additional states will be introduced as the product evolves.

---

# Monitoring Zones

Every thesis contains two primary monitoring zones.

## Opportunity Zone

Defined by:

Buy Range Low

Buy Range High

Purpose:

Notify the user that the predefined opportunity has appeared.

---

## Decision Zone

Defined by:

Stop Loss

Configurable buffer around the stop loss.

Purpose:

Notify the user that the original thesis may be weakening and a decision is approaching.

TradePilotAI does **not** recommend an action.

It only identifies that the thesis has reached a predefined decision point.

---

# Notification Philosophy

Notifications are generated when the thesis reaches meaningful decision points.

Examples include:

* Entering Buy Zone
* Leaving Buy Zone on the downside
* Entering Decision Zone
* Stop Loss reached
* Major scheduled event (future)
* Thesis invalidated (future)

Notifications should avoid duplication while ensuring important state changes are communicated.

---

# AI Responsibilities

The AI must remain an **independent analyst**.

It should never inherit or copy the user's thesis.

Instead, it should independently evaluate the market using available evidence.

AI responsibilities include:

* Building its own thesis
* Assigning an independent conviction score
* Identifying supporting evidence
* Identifying contradictory evidence
* Highlighting risks
* Comparing its thesis against the user's thesis

The AI acts as an external brain whose purpose is to strengthen, challenge, or validate the user's reasoning.

---

# User Responsibilities

The user owns the trading thesis.

The user defines:

* Buy Zone
* Stop Loss
* Initial reasoning
* Conviction score

TradePilotAI does not decide how a trade is executed.

Execution method (equity, options, CSPs, or any other instrument) is outside the scope of the Trade Thesis Specification.

TradePilotAI provides decision support, not trade execution.

---

# Guiding Principle

TradePilotAI exists to improve decision quality.

Its purpose is not to tell the user what to do.

Its purpose is to ensure that important opportunities, risks, and changes to a trade thesis are surfaced at the right time with the right context.

Every future feature should strengthen this objective.
