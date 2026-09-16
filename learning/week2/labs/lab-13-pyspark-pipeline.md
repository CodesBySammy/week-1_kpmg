# Lab 13: Distributed Transformations with PySpark

## Objective
Inspect and execute the standalone PySpark transformation pipeline in `pipeline/transformations/pyspark_lab.py`.

---

## Exercise

1. Inspect `pipeline/transformations/pyspark_lab.py`:
   Observe how Spark SQL functions (`F.col`, `F.when`, `F.to_utc_timestamp`) and `Window.partitionBy` translate our pandas transformations into distributed Spark execution DAGs.

2. Run the PySpark script (if PySpark/Java is available in your environment, or run via mock):
```bash
python -m pipeline.transformations.pyspark_lab
```

---

## Verification
- Notice how PySpark uses Catalyst logical and physical query optimization before triggering distributed execution.
