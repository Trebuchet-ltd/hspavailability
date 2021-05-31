async function get(url, kwargs = {}) {
    const response = await fetch(url + "?" + new URLSearchParams(kwargs), {
            headers: {'Content-Type': 'application/json'},
        }
    );
    return response.json()
}

async function post(url, kwargs = {}) {
    kwargs['csrfmiddlewaretoken'] = getCookie('csrftoken');
    const response = await fetch(url, {
            method: 'POST', // *GET, POST, PUT, DELETE, etc.
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(kwargs)
        }
    );
    return response.json()
}

async function patch(url, kwargs = {}) {
    kwargs['csrfmiddlewaretoken'] = getCookie('csrftoken');
    const response = await fetch(url, {
            method: 'PATCH', // *GET, POST, PUT, DELETE, etc.
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(kwargs)
        }
    );
    return response.json()
}

class ModelObject {
    data;
    baseUrl;
    id;
    fields;

    getData() {
        let self = this
        this.fields.forEach(item => {
            self[item] = self.data[item]
        })
    }

    constructor(data, baseUrl) {
        this.data = data
        this.id = data.id
        this.baseUrl = baseUrl

    }

    setData() {
        let self = this
        this.fields.forEach(item => {

            self.data[item] = self[item]
        })
    }

    save = async () => {
        this.setData()
        return patch(`${this.baseUrl}${this.id}/`, this.data)
    }

}

class Model {
    /**
     * @param {string} baseUrl
     * @param {ModelObject} modelClass
     */
    constructor(baseUrl, modelClass) {
        this.baseurl = baseUrl
        this.modelClass = modelClass
    }

    /**
     * @param {int} id
     * @param {{}} kwargs
     */
    get = async (id, kwargs = {}) => {
        let data = await get(`${this.baseurl}${id}/`, kwargs)
        return new this.modelClass(data, this.baseurl)

    };
    /**
     * @param {{}} kwargs
     */
    filter = async (kwargs = {}) => {
        let data = await get(`${this.baseurl}`, kwargs)
        let lst = []
        data.results.forEach(item => {
            lst.push(new this.modelClass(item, this.baseurl))
        })
        return {results: lst, next: data.next}
    };

    /**
     * @param {{}} kwargs
     */
    async create(kwargs = {}) {
        let data = await post(`${this.baseurl}`, kwargs)
        return new this.modelClass(data, this.baseurl)
    }
}

