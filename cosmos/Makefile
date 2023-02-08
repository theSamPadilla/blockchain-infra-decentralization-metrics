VERSION := $(shell echo $(shell git describe --tags) | sed 's/^v//')
COMMIT  := $(shell git log -1 --format='%H')

all: ci-lint ci-test install

###############################################################################
#                               Build / Install                               #
###############################################################################

LD_FLAGS = -X github.com/fissionlabsio/tmcrawl/cmd.Version=$(VERSION) \
	-X github.com/fissionlabsio/tmcrawl/cmd.Commit=$(COMMIT)

BUILD_FLAGS := -ldflags '$(LD_FLAGS)'

build: go.sum
ifeq ($(OS),Windows_NT)
	@echo "building tmcrawl binary..."
	@go build -mod=readonly $(BUILD_FLAGS) -o build/tmcrawl.exe .
else
	@echo "building tmcrawl binary..."
	@go build -mod=readonly $(BUILD_FLAGS) -o build/tmcrawl .
endif

install: go.sum
	@echo "installing tmcrawl binary..."
	@go install -mod=readonly $(BUILD_FLAGS) .

###############################################################################
#                                 Tests / CI                                  #
###############################################################################

coverage:
	@echo "viewing test coverage..."
	@go tool cover --html=coverage.out

ci-test:
	@echo "executing unit tests..."
	@go test -mod=readonly -v -coverprofile coverage.out ./... 

ci-lint:
	@echo "running GolangCI-Lint..."
	@GO111MODULE=on golangci-lint run
	@echo "formatting..."
	@find . -name '*.go' -type f -not -path "*.git*" | xargs goimports -w
	@echo "verifying modules..."
	@go mod verify

clean:
	rm -f tools-stamp ./build/**

###############################################################################
#                                   Docs                                      #
###############################################################################

swagger:
	@swag init --generatedTime=false -g server/swagger.go --output=server/docs

swagger-verify:
	@scripts/swag.sh

.PHONY: install build ci-test ci-lint swagger coverage clean
