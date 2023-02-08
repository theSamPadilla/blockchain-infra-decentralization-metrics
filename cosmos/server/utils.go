package server

func paginate(numObjs, page, limit, defLimit int) (start, end int) {
	if page == 0 {
		// invalid start page
		return -1, -1
	} else if limit == 0 {
		limit = defLimit
	}

	start = (page - 1) * limit
	end = limit + start

	if end >= numObjs {
		end = numObjs
	}

	if start >= numObjs {
		// page is out of bounds
		return -1, -1
	}

	return start, end
}
