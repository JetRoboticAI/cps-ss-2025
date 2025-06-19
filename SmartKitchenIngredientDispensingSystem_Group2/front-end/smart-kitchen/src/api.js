import axios from 'axios'
export const RECIPES = [
    { id: 1, name: 'sandwich', ingredients: ['A', 'B'] },
    { id: 2, name: 'burger', ingredients: ['A', 'C'] },
    { id: 3, name: 'chicken', ingredients: ['B', 'C', 'D'] },
    { id: 4, name: 'noodles', ingredients: ['A', 'D'] },
    { id: 5, name: 'rice', ingredients: ['B', 'D'] },
    { id: 6, name: 'beef', ingredients: ['A', 'B', 'C'] },
    { id: 7, name: 'vegetable', ingredients: ['C'] },
    { id: 8, name: 'egg', ingredients: ['D'] },
];

export const fetchRecipes = () => Promise.resolve({ data: RECIPES });
export const submitOrder = order =>
    axios.post('http://192.168.0.140:3001/api/orders', order)
        .then(res => res.data);

export const fetchOrders = () =>
    axios.get('http://192.168.0.140:3001/api/orders')
        .then(res => res.data);

