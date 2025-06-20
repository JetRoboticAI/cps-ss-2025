import React, { useEffect, useState } from 'react';
import { socket } from '../socket';
import { fetchOrders } from '../api';

export default function OrderStatus() {
    const [currentOrders, setCurrentOrders] = useState([]);
    const [historyOrders, setHistoryOrders] = useState([]);

    useEffect(() => {
        fetchOrders()
            .then(list => {
                const current = list.filter(o => o.status !== 'completed');
                const history = list.filter(o => o.status === 'completed');
                setCurrentOrders(current);
                setHistoryOrders(history);
            })
            .catch(err => console.error('Fetch orders error:', err));

        socket.on('orderStatus', msg => {
            setCurrentOrders(cur => {
                if (msg.status === 'completed') {
                    setHistoryOrders(hist => [msg, ...hist]);
                    return cur.filter(o => o.orderId !== msg.orderId);
                }
                const exists = cur.some(o => o.orderId === msg.orderId);
                return exists
                    ? cur.map(o => o.orderId === msg.orderId ? msg : o)
                    : [msg, ...cur];
            });
        });

        return () => socket.off('orderStatus');
    }, []);

    return (
        <div>
            <h1>Order Status</h1>
            <section>
                <h2>Current Order</h2>
                <ul>
                    {currentOrders.map((o, i) => (
                        <li key={i}>{`Order ${o.orderId}: ${o.status}`}</li>
                    ))}
                    {currentOrders.length === 0 && <li>No New Order</li>}
                </ul>
            </section>
            <section>
                <h2>History Order</h2>
                <ul>
                    {historyOrders.map((o, i) => (
                        <li key={i}>{`Order ${o.orderId}: ${o.status}`}</li>
                    ))}
                    {historyOrders.length === 0 && <li>No history Order</li>}
                </ul>
            </section>
        </div>
    );
}

