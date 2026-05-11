const baseURL =
  (typeof process !== 'undefined' && process.env && process.env.VUE_APP_API_BASE) ||
  'http://localhost:8000';

function getToken() {
  if (typeof uni !== 'undefined' && typeof uni.getStorageSync === 'function') {
    return uni.getStorageSync('token') || '';
  }
  return '';
}

function withQuery(url, params) {
  if (!params) return url;
  const keys = Object.keys(params);
  if (!keys.length) return url;

  const query = keys
    .filter((key) => params[key] !== undefined && params[key] !== null && params[key] !== '')
    .map((key) => encodeURIComponent(key) + '=' + encodeURIComponent(String(params[key])))
    .join('&');

  return query ? url + '?' + query : url;
}

function request(method, url, data, options) {
  const opts = options || {};
  const requestUrl = withQuery(baseURL + url, opts.params);
  const headers = Object.assign({}, opts.headers || {});
  const token = getToken();

  if (token) {
    headers.Authorization = 'Bearer ' + token;
  }

  return new Promise((resolve, reject) => {
    uni.request({
      url: requestUrl,
      method,
      data,
      header: headers,
      timeout: opts.timeout || 15000,
      success: (response) => {
        const code = response.statusCode || 0;
        if (code >= 200 && code < 400) {
          resolve({ data: response.data });
          return;
        }
        reject(response);
      },
      fail: reject
    });
  });
}

const api = {
  get(url, options) {
    return request('GET', url, undefined, options);
  },
  post(url, data, options) {
    return request('POST', url, data, options);
  },
  patch(url, data, options) {
    return request('PATCH', url, data, options);
  },
  delete(url, options) {
    return request('DELETE', url, undefined, options);
  }
};

export default api;
