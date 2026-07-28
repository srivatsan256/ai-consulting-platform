import React from "react";

export default function ClientProjectsPage(props){
return(<div className="min-h-screen p-8 bg-slate-50"><div className="bg-white rounded-xl shadow p-8"><h1 className="text-3xl font-bold">ClientProjectsPage</h1><p className="mt-3 text-gray-600">ClientProjectsPage Page</p>{props.projectId&&<p className="mt-4">Project ID: {props.projectId}</p>}{props.onBack&&<button onClick={props.onBack} className="mt-6 px-4 py-2 bg-indigo-600 text-white rounded">Back</button>}</div></div>);}
