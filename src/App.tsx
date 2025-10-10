import React from 'react';
import { Button } from './components/Button';
// import 
import './App.css';

function App() {
    return (
        <div className="CampaignMaster">
            <header className="CampaignMaster-Header">
                <h1>Campaign Master</h1>
            </header>
            <main className="CampaignMaster-Main">
                <Button title="Click Me" description="This is a button" onClick={() => alert('Button clicked!')} />
            </main>
        </div>
    )
}

export default App;
