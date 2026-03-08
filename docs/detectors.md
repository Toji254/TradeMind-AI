# Detector Notes

Each detector should be:

- explainable
- testable
- conservative in its claims
- able to show evidence
- able to produce coaching suggestions

## Output Contract

Every detector should return a `DetectionResult` containing:

- detector name
- pattern name
- confidence score
- summary
- evidence
- affected trade ids
- coaching suggestions

## MVP Detectors

### FOMO Buy
Heuristic examples:
- buy entered after rapid upward movement
- buy above short moving average threshold
- repeated losses after chasing green candles

### Panic Sell
Heuristic examples:
- sell into sharp downward movement
- exits near local weakness with poor follow-through outcome

### Revenge Trading
Heuristic examples:
- position size jumps after consecutive losses
- shortened cooldown after losses
- trade frequency spikes during drawdowns

### Time-of-Day Bias
Heuristic examples:
- loss concentration in specific hours
- overtrading during fatigue windows

### Streak Behavior
Heuristic examples:
- risk increase after wins
- tilt after losses
