// server.js
// -------------------------------
// 后端服务：接收订单 + 返回当前订单列表（含 CORS 解决方案）
// -------------------------------

const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const axios = require('axios');

const app = express();
const port = 5100;

// 设置允许跨域（允许来自 http://localhost:3000 的前端请求）
app.use(cors()); // 允许任意来源访问（不推荐上线使用）


app.use(bodyParser.json());

// 用于存储当前订单（内存版本）
const currentOrders = [];

// POST /orders - 接收前端提交订单并发送到树莓派
app.post('/orders', async (req, res) => {
    const order = req.body;
    console.log('接收到新订单:', order);
    currentOrders.push(order); // 存入内存

    try {
        // 暂时注释掉：发送到树莓派（防止连接错误影响前端）
        // await axios.post('http://192.168.0.140:8000/receive-order', order);
        res.status(200).json({ message: 'Order saved' });
    } catch (error) {
        console.error('发送订单到树莓派失败:', error.message);
        res.status(500).json({ message: '发送失败，请检查树莓派是否在线' });
    }
});

// GET /orders/current - 返回当前订单列表
app.get('/orders/current', (req, res) => {
    res.json(currentOrders);
});

// 启动服务
app.listen(port, () => {
    console.log(`后端服务运行在 http://localhost:${port}`);
});

