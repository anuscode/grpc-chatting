import sys
import pkg_resources

from grpc_tools import protoc


def update(name):
    proto_include = pkg_resources.resource_filename('grpc_tools', '_proto')

    protoc.main([
        "protoc",
        "--python_out=.",
        "--grpc_python_out=.",
        "./proto/{}.proto".format(name),
        "--proto_path=./proto/",
        "--proto_path={}".format(proto_include)
    ])


def main():
    update('chat')


if __name__ == '__main__':
    sys.exit(main())
