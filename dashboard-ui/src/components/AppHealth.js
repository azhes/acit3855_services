import React, { useEffect, useState } from 'react'
import '../App.css';

export default function HealthCheck() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [log, setLog] = useState(null);
    const [error, setError] = useState(null)
	const rand_val = Math.floor(Math.random() * 100); // Get a random event from the event store
    const [index, setIndex] = useState(null);

    const getAudit = () => {
        fetch(`http://acit3855kafka.westus3.cloudapp.azure.com/health/health`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Health Checks")
                setLog(result);
                setIsLoaded(true);
                setIndex(rand_val)
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
	useEffect(() => {
		const interval = setInterval(() => getAudit(), 20000); // Update every 20 seconds
		return() => clearInterval(interval);
    }, [getAudit]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        
        return (
            <div>
                {JSON.stringify(log)}
            </div>
        )
    }
}
