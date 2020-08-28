ARG image
FROM $image

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
WORKDIR /home/ci/dlisio/build
RUN cmake -DBUILD_SHARED_LIBS=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_NAME_DIR=/usr/local/lib -DPYTHON_EXECUTABLE=`which python3` ..
RUN make -j4
RUN ctest --output-on-failure
