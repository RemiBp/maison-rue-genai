import {facts} from '../lib/data.mjs';
export default function handler(req,res){res.setHeader('Cache-Control','no-store');return res.status(200).json(facts);}
