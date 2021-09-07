DOCKERHUB_IMAGE="galmenash/gofritools"
IMAGE_NAME="${IMAGE_NAME:-${DOCKERHUB_IMAGE}}"
CONTAINER_NAME="${CONTAINER_NAME:-gofritools}"
INSTALL_DIR="${INSTALL_DIR:-$(realpath ~/.local/bin)}"
UTIL_NAME="${UTIL_NAME:-gofritools}"

REPO="${REPO:-https://github.com/gofri/gofritools.git}"
BRANCH="${BRANCH:-master}"
PULL_DOCKERHUB=${PULL_DOCKERHUB:-1}
PULL_REPO=${PULL_REPO:-1}

LOCAL_SHORTCUTS_ONLY=${LOCAL_SHORTCUTS_ONLY:-0}

try_install_docker() {
    if grep -qi 'red hat' /etc/os-release; then
        sudo yum install -y podman && return 0
    else
        sudo apt install -y docker && return 0
    fi
    echo "Failed to get docker for you -- please install it yourself"
    return 1
}

get_installed_engine() {
    if grep -qi -e 'red hat' -e 'centos' -e 'fedora' /etc/os-release; then
        # rhel enable you to install both but always uses podman, which is fucked up.
        which podman && return 0
    fi
    which docker && return 0
    return 1
}

get_docker_engine() {
    engine="$()"
    if test -n "$engine"; then
        echo $engine;
        return 0;
    fi
    # try get - then try install - then try get again
    get_installed_engine || (try_install_docker && get_installed_engine)
}

main() {
    set -x

    # Install path
    if ! test -d "$INSTALL_DIR"; then
        INSTALL_DIR='/usr/bin/'
    fi

    # Engine discovery
    engine=$(get_docker_engine)
    if test -z "$engine"; then
        echo "Failed to get a docker engine -- please take care of it";
        exit 1
    fi

    if $LOCAL_SHORTCUTS_ONLY -eq 0; then

        # Cleanup
        $engine stop ${CONTAINER_NAME}
        $engine rm ${CONTAINER_NAME}
        $engine rmi ${IMAGE_NAME}

        # Build
        if test $PULL_DOCKERHUB -eq 1 && ${engine} pull ${DOCKERHUB_IMAGE}:latest; then
            IMAGE_NAME=${DOCKERHUB_IMAGE}
        else
            if test $PULL_DOCKERHUB -ne 1; then
                echo "Failed to pull -- let's build;"
            fi
            if test $PULL_REPO -eq 0; then
                $engine build --no-cache --build-arg branch=${BRANCH} -t "${IMAGE_NAME}"
            elif test "$engine" = "docker"; then
                $engine build --no-cache --build-arg branch=${BRANCH} -t "${IMAGE_NAME}" "${REPO}#${BRANCH}"
            else
                tmpdir=$(mktemp -d)
                (
                    cd $tmpdir
                    git clone -b $BRANCH $REPO tmp_repo 
                    cd tmp_repo 
                    $engine build --no-cache --build-arg branch=${BRANCH} -t "${IMAGE_NAME}" .
                )
                rm -rf $tmpdir
            fi
        fi
    fi

    # Installation
    UTIL="${INSTALL_DIR}/${UTIL_NAME}"
    __RUN_ARGS=''
    start_script="${engine} run -it -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix --detach --privileged -v /:/mnt/root --workdir /mnt/root\$(pwd) --name ${CONTAINER_NAME} ${IMAGE_NAME} bash"
    resume_script="${engine} start ${CONTAINER_NAME}"
    __exec_script="${engine} exec -it --workdir /mnt/root\$(pwd) ${CONTAINER_NAME}"
    exec_script="${__exec_script} gofritools \"\$@\""
    chmod +x "${UTIL}"

    (
        cd $INSTALL_DIR
        echo "$exec_script" > "${UTIL_NAME}"
        echo "if test -p /dev/stdout; then mode=p; else mode=b; fi; ${UTIL_NAME} \${mode} \"\$@\"" > gof
        echo "${UTIL_NAME} i \"\$@\"" > gofi
        echo "${UTIL_NAME} i g \"\$@\"" > gg
        echo "${UTIL_NAME} i f \"\$@\"" > ff
        echo "$start_script 2>/dev/null || $resume_script" > gof-start
        echo "$__exec_script bash -c '(cd /gofritools && git pull)'" > gof-update
        echo "$__exec_script bash -c '(cd /gofritools && git fetch && git reset --hard origin/master)'" > gof-force-update
        echo "$__exec_script bash" > gof-enter

        chmod +x gof gofi gg ff gof-start gof-update gof-force-update gof-enter
    )

    # Kick-off
    gof-start
}

main "$@"

