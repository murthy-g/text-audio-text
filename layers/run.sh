#!/bin/bash

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
pip install safetensors

# Create a virtual environment with Python 3.8
python3.8 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Clone and modify PyTorch source before loop
git clone https://github.com/pytorch/pytorch.git
pushd pytorch

# TODO: Manual pruning of unnecessary parts
# For now, just install from source
pip install . --target ../layers/torch/python

popd

# List of package groups to process
package_groups=(
    "transformers"
    "gtts soundfile boto3"
    "torchaudio pillow jsonify"
    "charset_normalizer urllib3"
)

for package_group in "${package_groups[@]}"; do
    group_name=$(echo "$package_group" | tr ' ' '_')
    echo "Downloading and processing group: $group_name"
    mkdir -p "./layers/$group_name/python"
    pushd "./layers/$group_name/python"

    pip install $package_group --target .

    # Special handling for transformers
    if [[ "$package_group" == "transformers" ]]; then
        echo "Slimming down transformers library..."
        rm -rf transformers/models/* 
        mkdir -p transformers/models/wav2vec2
        touch transformers/models/__init__.py
        cp -r [path_to_transformers_source_code]/models/wav2vec2/modeling_wav2vec2.py transformers/models/wav2vec2/
        cp -r [path_to_transformers_source_code]/models/wav2vec2/processors_wav2vec2.py transformers/models/wav2vec2/
    fi

    # Special handling for torchaudio
    if [[ "$package_group" == "torchaudio" ]]; then
        echo "Slimming down torchaudio library..."
        find torchaudio -type f ! -name '*resample*' -delete
    fi

    popd

    # Zip the package folders to create a layer zip file
    pushd "./layers"
    zip -r "$group_name".zip "$group_name"
    popd

    # Print the file size of the ZIP file
    echo "File size of $group_name.zip: $(du -h "./layers/$group_name.zip" | cut -f1)" >> test.txt

    # Upload the zipped layer to S3
    aws s3 cp "./layers/$group_name.zip" s3://zoom-api-layers/

    # Remove the package folders
    rm -r "./layers/$group_name"
    rm -rf "./layers"
done

# Deactivate the virtual environment
deactivate

# Optionally, remove the virtual environment
rm -r venv
