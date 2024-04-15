FROM chromadb/chroma:0.4.25.dev93

# Copy your modified requirements.txt file into the image
COPY requirements.chroma.txt /chroma/requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r /chroma/requirements.txt
