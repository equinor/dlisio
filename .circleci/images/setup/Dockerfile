FROM s390x/debian
RUN apt-get update
RUN apt-get install -y cmake g++ python3 python3-pip git

#mpark variant
WORKDIR /home/ci
RUN git clone https://github.com/mpark/variant.git
WORKDIR /home/ci/variant/build
RUN cmake -DCMAKE_BUILD_TYPE=Release ..
RUN make -j4
RUN make install

#fmt
WORKDIR /home/ci
RUN git clone https://github.com/fmtlib/fmt.git
WORKDIR /home/ci/fmt/build
RUN cmake -DFMT_TEST=OFF -DFMT_DOC=OFF ..
RUN make -j4
RUN make install

#dlisio_requirements
WORKDIR /home/ci
COPY . /home/ci/dlisio_requirements
WORKDIR /home/ci/dlisio_requirements
RUN python3 -m pip install --user -r python/requirements-dev.txt
