# #!/bin/bash

# # List of package pairs to process
# package_pairs=(
#     "gtts"
# )

# for package_pair in "${package_pairs[@]}"; do
#     # Extract the package names from the pair
#     package_name1=$(echo "$package_pair" | cut -d' ' -f1)
#     package_name2=$(echo "$package_pair" | cut -d' ' -f2)
    
#     echo "Downloading $package_name1 and $package_name2"
#     # Create a folder for the package and navigate into it
#     mkdir "$package_name1-$package_name2"
#     pushd "$package_name1-$package_name2"

#     # Download the packages
#     pip download "$package_name1"
#     pip download "$package_name2"

#     # Unzip the downloaded packages
#     unzip "$package_name1".*.zip
#     rm "$package_name1".*.zip
#     unzip "$package_name2".*.zip
#     rm "$package_name2".*.zip

#     # Navigate back to the parent directory
#     popd

#     # Zip the package folders to create a layer zip file
#     zip -r "$package_name1-$package_name2".zip "$package_name1-$package_name2"

#     # Print the file size of the ZIP file
#     echo "File size of $package_name1-$package_name2.zip: $(du -h "$package_name1-$package_name2.zip" | cut -f1)" >> test.txt

#     # Remove the package folders (optional, depending on your use case)
#     rm -r "$package_name1-$package_name2"
# done
#install only python3.8

# python3.8 -m venv venv
# source venv/bin/activate
# pip install --upgrade pip
# mkdir python
# cd python
# pip install gtts
# # deactivate
# cd ..
# zip -r gtts.zip .

#!/bin/bash

#!/bin/bash

# Create layers for gtts, urllib3, boto3
mkdir -p layers/layer1/gtts_layer/python/lib/python3.11/site-packages 
pip install gtts -t layers/layer1/gtts_layer/python/lib/python3.11/site-packages --no-deps --no-build-isolation

mkdir -p layers/layer1/urllib3_layer/python/lib/python3.11/site-packages
pip install urllib3 -t layers/layer1/urllib3_layer/python/lib/python3.11/site-packages --no-deps --no-build-isolation

mkdir -p layers/layer1/boto3_layer/python/lib/python3.11/site-packages
pip install boto3 -t layers/layer1/boto3_layer/python/lib/python3.11/site-packages --no-deps --no-build-isolation

# Zip the layers
cd layers/layer1/gtts_layer
zip -r ../gtts_layer.zip .
rm -rf layers/layer1/gtts_layer

cd ../urllib3_layer
zip -r ../urllib3_layer.zip .
rm -rf layers/layer1/urllib3_layer

cd ../boto3_layer
zip -r ../boto3_layer.zip .
rm -rf layers/layer1/boto3_layer

cd ../../..

# Create layers for transformers, torch, soundfile, torchaudio
mkdir -p layers/layer2/transformers_layer/python/lib/python3.11/site-packages
pip install transformers -t layers/layer2/transformers_layer/python/lib/python3.11/site-packages --no-deps --no-build-isolation

mkdir -p layers/layer2/torch_layer/python/lib/python3.11/site-packages
pip install torch -t layers/layer2/torch_layer/python/lib/python3.11/site-packages --no-deps --no-build-isolation

mkdir -p layers/layer2/soundfile_layer/python/lib/python3.11/site-packages
pip install soundfile -t layers/layer2/soundfile_layer/python/lib/python3.11/site-packages --no-deps --no-build-isolation

mkdir -p layers/layer2/torchaudio_layer/python/lib/python3.11/site-packages
pip install torchaudio -t layers/layer2/torchaudio_layer/python/lib/python3.11/site-packages --no-deps --no-build-isolation

# Zip the layers
cd layers/layer2/transformers_layer
zip -r ../transformers_layer.zip .
rm -rf layers/layer2/transformers_layer

cd ../torch_layer
zip -r ../torch_layer.zip .
rm -rf layers/layer2/torch_layer

cd ../soundfile_layer
zip -r ../soundfile_layer.zip .
rm -rf layers/layer2/soundfile_layer

cd ../torchaudio_layer
zip -r ../torchaudio_layer.zip .
rm -rf layers/layer2/torchaudio_layer

# Clean up
cd ../..
