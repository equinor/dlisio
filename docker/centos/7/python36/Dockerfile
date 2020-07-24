FROM centos/python-36-centos7
USER 0:0
RUN pip install --upgrade pip
WORKDIR /work
RUN yum install -y make gcc g++ libc-dev linux-headers boost-dev git wget
RUN yum install -y epel-release && yum install -y cmake3
WORKDIR /work
RUN git clone https://github.com/ejschoen/dlisio.git && cd dlisio && git checkout master && git submodule update --init external/fmt && git submodule update --init external/mpark 
RUN git clone https://github.com/fmtlib/fmt.git
RUN git clone https://github.com/equinor/layered-file-protocols.git
RUN pip install pybind11 scikit-build numpy chardet 
WORKDIR /work/fmt/build
RUN cmake3 -DFMT_TEST=OFF -DFMT_DOC=OFF .. -DBUILD_SHARED_LIBS=ON && make && make install
WORKDIR /work/layered-file-protocols/build
RUN cmake3 -DBUILD_SHARED_LIBS=ON -DLFP_FMT_HEADER_ONLY=ON -DBUILD_TESTING=OFF -DCMAKE_BUILD_TYPE=Release .. && make && make install
WORKDIR /work/dlisio/build
RUN cmake3 .. -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON -DMAKE_EXPORT_COMPILE_COMMANDS=ON -DPYTHON_EXECUTABLE=/opt/app-root/bin/python3 && cd .. && cmake3 --build build --target install
WORKDIR /work/dlisio
RUN pip install --upgrade -r python/requirements-dev.txt && bandit -c bandit.yml -r python
WORKDIR /work/dlisio/python
RUN mkdir -p wheelhouse && rm -rf _skbuild && pip wheel -w wheelhouse --no-deps .
