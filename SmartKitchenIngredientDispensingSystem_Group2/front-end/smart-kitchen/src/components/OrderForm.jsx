import React, { useState, useEffect } from 'react';

const OrderForm = () => {
    const [dish, setDish] = useState('sandwich');
    const [ingredients, setIngredients] = useState({ A: false, B: false, C: false, D: false });
    const [message, setMessage] = useState('');
    const [orders, setOrders] = useState([]);

    const handleCheckboxChange = (e) => {
        const { name, checked } = e.target;
        setIngredients((prev) => ({ ...prev, [name]: checked }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const selectedIngredients = Object.keys(ingredients).filter((key) => ingredients[key]);
        if (selectedIngredients.length === 0) {
            setMessage('Choose the ingredients Please');
            return;
        }

        const order = {
            dish,
            ingredients: selectedIngredients,
        };

        try {
            const res = await fetch('http://localhost:5100/orders', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(order),
            });
            const data = await res.json();
            setMessage(data.message);
            fetchOrders();
        } catch (error) {
            console.error('submit fail', error);
            setMessage('submit fail');
        }
    };
    // 拉取当前订单列表
    const fetchOrders = async () => {
        try {
            const res = await fetch('http://localhost:5100/orders/current');
            const data = await res.json();
            setOrders(data);
        } catch (err) {
            console.error('order fail', err);
        }
    };

    useEffect(() => {
        fetchOrders();
        const interval = setInterval(fetchOrders, 5100); // 每 5 秒刷新一次
        return () => clearInterval(interval);
    }, []);

    return (
        <div style={{ padding: '1rem' }}>
            <form onSubmit={handleSubmit} style={{ border: '1px solid #ccc', marginBottom: '1rem' }}>
                <h2>Make an Order</h2>
                <label>
                    Choose a Product：
                    <select value={dish} onChange={(e) => setDish(e.target.value)}>
                        <option value="sandwich">Sandwich</option>
                        <option value="burger">Burger</option>
                        <option value="chicken">Chicken</option>
                        <option value="noodles">Noodles</option>
                        <option value="rice">Rice</option>
                        <option value="beef">Beef</option>
                        <option value="vegetable">Vegetable</option>
                        <option value="egg">Egg</option>
                    </select>
                </label>

                <div>
                    <p>Choose ingredients：</p>
                    {['A', 'B', 'C', 'D'].map((key) => (
                        <label key={key}>
                            <input
                                type="checkbox"
                                name={key}
                                checked={ingredients[key]}
                                onChange={handleCheckboxChange}
                            />
                            Ingredients {key}
                        </label>
                    ))}
                </div>

                <button type="submit">Submit Order</button>

                {message && <p>{message}</p>}
            </form>

            <div style={{ border: '1px solid #ccc', padding: '1rem' }}>
                <h2>Current Order</h2>
                {orders.length === 0 ? (
                    <p>No Order now</p>
                ) : (
                    <ul>
                        {orders.map((order, index) => (
                            <li key={index}>
                                <strong>{order.dish}</strong> - ingredients: {order.ingredients.join(', ')}
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
};

export default OrderForm;
