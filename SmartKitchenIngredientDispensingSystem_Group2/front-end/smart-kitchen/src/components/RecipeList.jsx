import React, { useEffect, useState } from 'react';
import { fetchRecipes } from '../api';

export default function RecipeList({ onSelect }) {
    const [recipes, setRecipes] = useState([]);

    useEffect(() => {
        fetchRecipes()
            .then(res => setRecipes(res.data))
            .catch(err => console.error('Fetch recipes error:', err));
    }, []);

    return (
        <div>
            <h1>products</h1>
            <ul>
                {recipes.map(r => (
                    <li key={r.id} style={{ margin: '8px 0' }}>
                        <button onClick={() => onSelect(r)}>
                            {r.name}
                        </button>
                        <div>ingredients:{r.ingredients.join(',')}</div>
                    </li>
                ))}
            </ul>
        </div>
    );
}
