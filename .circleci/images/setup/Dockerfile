FROM s390x/debian
RUN apt-get update
RUN apt-get install -y cmake g++ python3 python3-pip git

#fmt
WORKDIR /home/ci
RUN git clone https://github.com/fmtlib/fmt.git
WORKDIR /home/ci/fmt/build
RUN cmake ..
RUN make -j4
RUN make install

#dlisio_requirements
WORKDIR /home/ci
COPY . /home/ci/dlisio_requirements
WORKDIR /home/ci/dlisio_requirements
RUN python3 -m pip install --user -r python/requirements-dev.txt
