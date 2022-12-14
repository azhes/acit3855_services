import logo from './logo.png';
import './App.css';

import EndpointAudit from './components/EndpointAudit'
import AppStats from './components/AppStats'
import HealthCheck from './components/AppHealth';

function App() {

    const endpoints = ["posttrade", "accepttrade"]

    const rendered_endpoints = endpoints.map((endpoint) => {
        return <EndpointAudit key={endpoint} endpoint={endpoint}/>
    })

    const healthCheck = HealthCheck()

    return (
        <div className="App">
            <img src={logo} className="App-logo" alt="logo" height="300px" width="400px"/>
            <div>
                <AppStats/>
                <h1>Audit Endpoints</h1>
                {rendered_endpoints}
                <h1>Health Check</h1>
                {healthCheck}
            </div>
        </div>
    );

}



export default App;
