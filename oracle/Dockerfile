FROM tensorflow/tensorflow

WORKDIR /usr/src/app

COPY requirements.txt ./
# COPY tensorflow-2.12.0-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl ./tensorflow-2.12.0-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
# RUN pip install --no-cache-dir tensorflow-2.12.0-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-u", "./run.py" ]