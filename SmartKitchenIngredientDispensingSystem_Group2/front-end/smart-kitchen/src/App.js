import React, { useState } from 'react';
import RecipeList from './components/RecipeList.jsx';
import OrderForm from './components/OrderForm.jsx';
import OrderStatus from './components/OrderStatus.jsx';
import logo from './logo.svg';
import './App.css';

function App() {
  const [selected, setSelected] = useState(null);

  const handleSelect = recipe => setSelected(recipe);
  const handleBack = () => setSelected(null);
  return (
    <div className="App" style={{ padding: '16px' }}>
      {selected
        ? <OrderForm recipe={selected} onBack={() => setSelected(null)} />
        : <RecipeList onSelect={setSelected} />
      }
      <hr />
      <OrderStatus />
    </div>
  );
}

export default App;


