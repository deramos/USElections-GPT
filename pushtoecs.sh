#!/bin/bash

# Define the ECR repository URL
ECR_REPOSITORY_URL="697335112974.dkr.ecr.us-east-1.amazonaws.com"

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REPOSITORY_URL

# Get the list of all Docker images with "us-election" in their name
images=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "uselections")

# Check if any images were found
if [ -z "$images" ]; then
  echo "No images found with 'uselections' in the name."
  exit 1
fi

# Loop through the images and tag them with the ECR URL
for image in $images; do
  # Extract the image name and tag
  image_name=$(echo $image | cut -d ':' -f 1)
  image_tag=$(echo $image | cut -d ':' -f 2)

  # Construct the new ECR tag
  ecr_tag="${ECR_REPOSITORY_URL}/${image_name}:${image_tag}"

  # Tag the image
  echo "Tagging image $image as $ecr_tag"
  docker tag $image $ecr_tag

  # Optionally, push the image to ECR
  # echo "Pushing image $ecr_tag to ECR"
  docker push $ecr_tag
done
