export function normalizeQuery (query) {
	// given a string such as 'this is "my query" go', returns
	// an array of tokens like this: ['this', 'is', 'my query', 'go']
	if (!query) {
		return []
	}
	return query.match(/\\?.|^$/g).reduce((p, c) => {
		if (c === '"'){
			p.quote ^= 1
		} else if (!p.quote && c === ' '){
			p.a.push('')
		} else {
			p.a[p.a.length-1] += c.replace(/\\(.)/,"$1")
		}
		return p
	}, {a: ['']}).a
}

export function parseTokens (tokens) {
	// given an array of tokens as returned by normalizeQuery,
	// returns a list of objects such as [
	// 	{
	// 		field: 'status',
	// 		value: 'pending'
	// 	},
	// 	{
	// 		field: null,
	// 		value: 'hello'
	// 	}
	// ]
	return tokens.map(t => {
		// we split the token on ":"
		let parts = t.split(/:(.+)/)
		if (parts.length === 1) {
			// no field specified
			return {field: null, value: t}
		}
		// first item is the field, second is the value, possibly quoted
		let field = parts[0]
		let rawValue = parts[1]

		// we remove surrounding quotes if any
		if (rawValue[0] === '"') {
			rawValue = rawValue.substring(1)
		}
		if (rawValue.slice(-1) === '"') {
			rawValue = rawValue.substring(0, rawValue.length - 1);
		}
		return {field, value: rawValue}
	})
}

export function compileTokens (tokens) {
  // given a list of tokens as returned by parseTokens,
  // returns a string query
  let parts = tokens.map(t => {
    let v = t.value
    let k = t.field
    if (v.indexOf(' ') > -1) {
      v = `"${v}"`
    }
    if (k) {
      return `${k}:${v}`
    } else {
      return v
    }
  })
  return parts.join(' ')
}
