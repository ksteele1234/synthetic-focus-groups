# Persona Weighting Test Cases

These test cases demonstrate correct persona weighting in aggregation tasks.

## Test Case 1: Simple Weighted Aggregation
- Personas: A (weight 2.0), B (weight 1.0)
- Insights: A = 10, B = 20
- Expected aggregate: (2.0*10 + 1.0*20) / (2.0+1.0) = 13.33

## Test Case 2: Zero Weight Persona
- Personas: A (weight 0.0), B (weight 1.0)
- Insights: A = 50, B = 30
- Expected aggregate: (0.0*50 + 1.0*30) / (0.0+1.0) = 30

## Test Case 3: All Equal Weights
- Personas: A (weight 1.0), B (weight 1.0), C (weight 1.0)
- Insights: A = 5, B = 10, C = 15
- Expected aggregate: (1.0*5 + 1.0*10 + 1.0*15) / 3.0 = 10

## Test Case 4: Mixed Weights and Insights
- Personas: A (weight 3.0), B (weight 1.0), C (weight 2.0)
- Insights: A = 8, B = 12, C = 6
- Expected aggregate: (3.0*8 + 1.0*12 + 2.0*6) / (3.0+1.0+2.0) = 8

## Test Case 5: Negative Weights (should be handled as error)
- Personas: A (weight -1.0), B (weight 2.0)
- Insights: A = 10, B = 20
- Expected: Error or validation failure

---
