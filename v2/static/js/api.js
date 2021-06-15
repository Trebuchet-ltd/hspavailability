async function get(url, kwargs = {}) {
    const response = await fetch(url + "?" + new URLSearchParams(kwargs), {
            headers: {'Content-Type': 'application/json'},
        }
    );
    return response.json()
}

async function post(url, kwargs = {}) {
    kwargs['csrfmiddlewaretoken'] = csrf;
    const response = await fetch(url, {
            method: 'POST', // *GET, POST, PUT, DELETE, etc.
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf
            },
            body: JSON.stringify(kwargs)
        }
    );
    if (response.status > 300) {
        throw (response)
    } else {

        console.log(response)
        return response.json()
    }
}

async function patch(url, kwargs = {}) {
    kwargs['csrfmiddlewaretoken'] = csrf;
    const response = await fetch(url, {
            method: 'PATCH', // *GET, POST, PUT, DELETE, etc.
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf
            },
            body: JSON.stringify(kwargs)
        }
    );
    if (response.status > 300) {
        throw (response)
    } else {

        console.log(response)
        return response.json()
    }
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
        try {
            let data = await patch(`${this.baseUrl}${this.id}/`, this.data)
            return new this.constructor(data, this.baseUrl)
        } catch (e) {
            let errors;
            errors = await e.json()
            console.log(errors)
            throw errors

        }
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
        try {
            let data = await post(`${this.baseurl}`, kwargs)
            return new this.modelClass(data, this.baseurl)
        } catch (e) {
            let errors;
            errors = await e.json()
            console.log(errors)
            throw errors

        }
    }

}

