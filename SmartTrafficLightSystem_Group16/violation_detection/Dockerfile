# Use Ubuntu 24.04 as the base image
FROM ubuntu:24.04

# Copy your executable or project files into the container
# https://github.com/M4TH1EU/easy-local-alpr
COPY easy-local-alpr-1.5.0-openvinocpu_linux_x86_64 /usr/local/bin/

# Optional: Install any additional dependencies
# RUN apt-get install -y <other_dependencies>

# Expose port 5000
EXPOSE 5000

# Run your application when the container starts
CMD ["easy-local-alpr-1.5.0-openvinocpu_linux_x86_64"]

