
package main

import (
    "dagger.io/dagger"
    "universe.dagger.io/docker"
)

dagger.#Plan & {
    
    client: {
        filesystem: {
            "./": read: contents: dagger.#FS
            "./mondaydotcom_utils": write: contents: actions.clean.black.export.directories."/workdir/mondaydotcom_utils"
            "./tests": write: contents: actions.clean.black.export.directories."/workdir/tests"
            "./htmlcov": write: contents: actions.test.pytest.export.directories."/workdir/htmlcov"
        }
    }
    python_version: string | *"3.9"
    poetry_version: string | *"1.1.13"

    actions: {
        // referential build for base python image
        python_pre_build: docker.#Build & {
            steps: [
                docker.#Pull & {
                    source: "python:" + python_version
                },
                docker.#Run & {
                    command: {
                        name: "mkdir"
                        args: ["/workdir"]
                    }
                },
                docker.#Copy & {
                    contents: client.filesystem."./".read.contents
                    source:"./pyproject.toml"
                    dest: "/workdir/pyproject.toml"
                },
                docker.#Copy & {
                    contents: client.filesystem."./".read.contents
                    source:"./poetry.lock"
                    dest: "/workdir/poetry.lock"
                },
                docker.#Run & {
                    workdir: "/workdir"
                    command: {
                        name: "pip"
                        args: ["install","--no-cache-dir","poetry==" + poetry_version]
                    }
                },
                docker.#Set & {
                    config: {
                        env: ["POETRY_VIRTUALENVS_CREATE"] : "false"
                    }
                },
                docker.#Run & {
                    workdir: "/workdir"
                    command: {
                        name: "poetry"
                        args: ["install", "--no-interaction", "--no-ansi"]
                    }
                },
            ]
        }
        // python build for actions in this plan
        python_build: docker.#Build & {
            steps:[
                docker.#Copy & {
                    input: python_pre_build.output
                    contents: client.filesystem."./".read.contents
                    source:"./"
                    dest: "/workdir"
                }
            ]
        }
        // applied code and/or file formatting
        clean: {
            // sort python imports with isort
            isort: docker.#Run & {
                input: python_build.output
                workdir: "/workdir"
                command: {
                    name: "poetry"
                    args: ["run", "isort", "mondaydotcom_utils/", "tests/"]
                }
            }
            // code style formatting with black
            black: docker.#Run & {
                input: isort.output
                workdir: "/workdir"
                command: {
                    name: "poetry"
                    args: ["run", "black", "mondaydotcom_utils/", "tests/"]
                }
                export: {
                    directories: {
                        "/workdir/mondaydotcom_utils": _
                        "/workdir/tests": _
                    }
                }
            }
        }
        // lint
        lint: {
            // mypy static type check
            mypy: docker.#Run & {
                input: python_build.output
                workdir: "/workdir"
                command: {
                    name: "poetry"
                    args: ["run", "mypy", "--ignore-missing-imports", "mondaydotcom_utils/"]
                }
            }
            // isort (imports) formatting check
            isort: docker.#Run & {
                input: mypy.output
                workdir: "/workdir"
                command: {
                    name: "poetry"
                    args: ["run", "isort", "--check", "--diff mondaydotcom_utils/", "tests/"]
                }
            }
            // black formatting check
            black: docker.#Run & {
                input: isort.output
                workdir: "/workdir"
                command: {
                    name: "poetry"
                    args: ["run", "black", "--check", "mondaydotcom_utils/", "tests/"]
                }
            }
            // pylint checks
            pylint: docker.#Run & {
                input: black.output
                workdir: "/workdir"
                command: {
                    name: "poetry"
                    args: ["run", "pylint", "mondaydotcom_utils/", "tests/"]
                }
            }
            // safety security vulnerabilities check
            safety: docker.#Run & {
                input: pylint.output
                workdir: "/workdir"
                command: {
                    name: "poetry"
                    args: ["run", "safety", "check"]
                }
            }
            // bandit security vulnerabilities check
            bandit: docker.#Run & {
                input: safety.output
                workdir: "/workdir"
                command: {
                    name: "poetry"
                    args: ["run", "bandit", "-r", "mondaydotcom_utils/"]
                }
            }
        }
        test: {
            // run pytest tests
            pytest: docker.#Run & {
                input: python_build.output
                workdir: "/workdir"
                command: {
                    name: "poetry"
                    args: ["run", "pytest", "-s", "--cov=mondaydotcom_utils/", 
                            "--cov=tests", "--cov-report", "html"]
                }
                export: {
                    directories: "/workdir/htmlcov": _
                }
            }
        }
    }
}

