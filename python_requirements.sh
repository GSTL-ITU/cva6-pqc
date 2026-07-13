# Update the loop in your python_requirements.sh script:
for req_file in $(find . -name "requirements.txt"); do
    echo "   Installing: $req_file"
    # Force pure-python build for ruamel.yaml to avoid C-API errors
    RUAMEL_NO_EXTENSION=1 pip3 install --user -r "$req_file"
done