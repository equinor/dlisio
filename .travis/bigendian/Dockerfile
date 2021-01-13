FROM s390x/debian
RUN apt-get update
# some needed python libraries are installed as part of recommendations
RUN apt-get install -y make cmake g++ python3 python3-pip python3-setuptools git

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

#lfp
WORKDIR /home/ci
RUN git clone https://github.com/equinor/layered-file-protocols.git
WORKDIR /home/ci/layered-file-protocols/build
RUN cmake -DBUILD_SHARED_LIBS=ON -DLFP_FMT_HEADER_ONLY=ON -DCMAKE_INSTALL_NAME_DIR=/usr/local/lib -DBUILD_TESTING=OFF -DCMAKE_BUILD_TYPE=Release ..
RUN make -j4
RUN make install

#dlisio
WORKDIR /home/ci
COPY . /home/ci/dlisio
WORKDIR /home/ci/dlisio
RUN python3 -m pip install --user -r python/requirements-dev.txt
WORKDIR /home/ci/dlisio/build
RUN cmake -DBUILD_SHARED_LIBS=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_NAME_DIR=/usr/local/lib -DPYTHON_EXECUTABLE=`which python3` ..
RUN make -j4
RUN ctest --output-on-failure
