python3.8 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install Flask requests jsonify torch transformers soundfile torchaudio boto3

python3.8 -m venv .env
source .env/bin/activate
pip install --upgrade pip
pip install --upgrade aws-cdk.core aws-cdk.aws-apigateway aws-cdk.aws-lambda aws-cdk.aws-s3 aws-cdk.aws-s3-deployment boto3
pip install -r requirements.txt
pip install aws-cdk-lib==2.90.0
pip install constructs==10.2.69
pip install --upgrade aws-cdk-lib
