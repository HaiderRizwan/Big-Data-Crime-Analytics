FROM public.ecr.aws/bitnami/spark:3.5

USER root
RUN pip install --no-cache-dir pandas numpy scikit-learn psycopg2-binary pymongo pyyaml

USER 1001
