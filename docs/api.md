# API Foundations

## Overview

Request/response validation in `quantsmind.api`: pydantic models for
polynomial, matrix, optimization, and simulation operations, plus
FastAPI endpoint definitions.

## Purpose

Let integrators validate SDK inputs at system boundaries with typed
errors instead of ad-hoc checks.

## Concept

`*Request` models whitelist operations via validators; `*Endpoints`
expose them over HTTP; `APIResponse`/`HealthResponse` standardize
outputs.

## API

`PolynomialRequest`, `MatrixRequest`, `OptimizationRequest`,
`SimulationRequest`, `APIResponse`, `HealthResponse`,
endpoint classes, `router`.

## Input / Processing / Output

Input: operation payloads. Processing: pydantic validation.
Output: typed models or `ValidationError`.

## Example

`python examples/api/request_models.py` builds valid requests and shows
one rejection (needs `pydantic>=2`).

## Limitations

Optional extra (`quantsmind[api]`); endpoint serving needs FastAPI,
which the `api` extra does not currently declare — install it
separately until the extra is corrected.
