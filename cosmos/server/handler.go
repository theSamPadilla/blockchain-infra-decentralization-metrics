package server

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"

	"github.com/gorilla/mux"
	httpswagger "github.com/swaggo/http-swagger"
	"github.com/theSamPadilla/tmcrawl/crawl"
	"github.com/theSamPadilla/tmcrawl/db"
	_ "github.com/theSamPadilla/tmcrawl/server/docs"
)

const (
	methodGET = "GET"
)

// RegisterRoutes registers all HTTP routes with the provided mux router.
func RegisterRoutes(db db.DB, r *mux.Router) {
	r.PathPrefix("/swagger/").Handler(httpswagger.WrapHandler)
	r.HandleFunc("/api/v1/nodes", getNodesHandler(db)).Methods(methodGET)
	r.HandleFunc("/api/v1/nodes/{address}", getNodeHandler(db)).Methods(methodGET)
}

// PaginatedNodesResp defines a paginated search result of nodes.
type PaginatedNodesResp struct {
	Total int          `json:"total" yaml:"total"`
	Page  int          `json:"page" yaml:"page"`
	Limit int          `json:"limit" yaml:"limit"`
	Nodes []crawl.Node `json:"nodes" yaml:"nodes"`
}

// @Summary Get all nodes
// @Description Get all nodes with optional pagination query parameters.
// @Tags nodes
// @Produce json
// @Param page query int false "The page number to query"
// @Param limit query int false "The number of nodes per page"
// @Success 200 {object} server.PaginatedNodesResp
// @Failure 400 {object} server.ErrorResponse "Invalid pagination parameters or failure to parse a node"
// @Router /nodes [get]
func getNodesHandler(db db.DB) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		pageStr := r.FormValue("page")
		limitStr := r.FormValue("limit")

		page := 1
		limit := 0

		if pageStr != "" {
			x, _ := strconv.Atoi(pageStr)
			if x <= 0 {
				writeErrorResponse(w, http.StatusBadRequest, fmt.Errorf("invalid page query: %s", pageStr))
				return
			}

			page = x
		}

		if limitStr != "" {
			x, _ := strconv.Atoi(limitStr)
			if x <= 0 {
				writeErrorResponse(w, http.StatusBadRequest, fmt.Errorf("invalid limit query: %s", limitStr))
				return
			}

			limit = x
		}

		nodes := []crawl.Node{}
		total := 0

		var err error
		db.IteratePrefix(crawl.NodeKeyPrefix, func(_, v []byte) bool {
			node := new(crawl.Node)
			err = node.Unmarshal(v)

			if err != nil {
				return true
			}

			total += 1
			nodes = append(nodes, *node)

			return false
		})

		if err != nil {
			writeErrorResponse(w, http.StatusBadRequest, fmt.Errorf("failed to query nodes: %w", err))
			return
		}

		start, end := paginate(len(nodes), page, limit, len(nodes))
		if start < 0 || end < 0 {
			nodes = []crawl.Node{}
		} else {
			nodes = nodes[start:end]
		}

		resp := PaginatedNodesResp{
			Page:  page,
			Limit: limit,
			Total: total,
			Nodes: nodes,
		}

		bz, err := json.Marshal(resp)
		if err != nil {
			writeErrorResponse(w, http.StatusBadRequest, fmt.Errorf("failed to encode response: %w", err))
			return
		}

		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(bz)
	}
}

// @Summary Get node
// @Description Get node by address.
// @Tags nodes
// @Produce json
// @Param address path string true "The node address (IP or resolvable to IP)"
// @Success 200 {object} crawl.Node
// @Failure 400 {object} server.ErrorResponse "Failure to parse the node"
// @Failure 404 {object} server.ErrorResponse "Failure to find the node"
// @Router /nodes/{address} [get]
func getNodeHandler(db db.DB) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		address := vars["address"]

		if !db.Has(crawl.NodeKey(address)) {
			writeErrorResponse(w, http.StatusNotFound, fmt.Errorf("failed to find node: %s", address))
			return
		}

		bz, _ := db.Get(crawl.NodeKey(address))

		node := new(crawl.Node)
		if err := node.Unmarshal(bz); err != nil {
			writeErrorResponse(w, http.StatusBadRequest, fmt.Errorf("failed to decode node: %w", err))
			return
		}

		bz, err := json.Marshal(node)
		if err != nil {
			writeErrorResponse(w, http.StatusBadRequest, fmt.Errorf("failed to encode response: %w", err))
			return
		}

		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(bz)
	}
}
