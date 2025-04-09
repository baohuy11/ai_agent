import { useLoaction, useNavigate, Link } from 'react-route-domm';
function NavBar(){
    const navigate = useNavigate();
    const loaction = useLoaction();
    return (
        <div className="navbar bg-base-100 w-[95%]">
            <div className="navbar-start">
                <div className="dropdown">
                    <label tabIndex={0} className="btn btn-ghost lg:hidden">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="w-5 h-5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M4 6h16M4 12h16m-7 6h7"
                            />
                        </svg>
                    </label>
                    <ul
                        tabIndex={0}
                        className="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52"
                    >
                        <li>
                            <Link to="/" className="btn btn-ghost">
                                <a>Home Page</a>
                            </Link>
                        </li>
                        <li>
                            <Link to="/chat">
                                <a>Chat Bot</a>
                            </Link>
                        </li>
                        <li>
                            <Link to="/info">
                                <a>Information</a>
                            </Link>
                        </li>
                        <li>
                            <Link to="/faq">
                                <a>FAQs</a>
                            </Link>
                        </li>
                        <li>
                            <Link to="/issue">
                                <a>Error Report</a>
                            </Link>
                        </li>
                    </ul>
                </div>
                <a  onClick={()=>navigate("/")}  className="btn btn-ghost normal-case font-extrabold text-xl bg-[linear-gradient(90deg,hsl(var(--s))_0%,hsl(var(--sf))_9%,hsl(var(--pf))_42%,hsl(var(--p))_47%,hsl(var(--a))_100%)] bg-clip-text will-change-auto [-webkit-text-fill-color:transparent] [transform:translate3d(0,0,0)] motion-reduce:!tracking-normal max-[1280px]:!tracking-normal [@supports(color:oklch(0_0_0))]:bg-[linear-gradient(90deg,hsl(var(--s))_4%,color-mix(in_oklch,hsl(var(--sf)),hsl(var(--pf)))_22%,hsl(var(--p))_45%,color-mix(in_oklch,hsl(var(--p)),hsl(var(--a)))_67%,hsl(var(--a))_100.2%)]">
                HealCare Chatbot
                </a>
            </div>
            <div className="navbar-center hidden lg:flex">
                <ul className="menu menu-horizontal px-1 font-semibold">
                    <li className='p-1'>
                        <button onClick={()=>navigate("/")} className={loaction.pathname=="/"?"btn btn-outline btn-primary":""}>Home Page</button>
                    </li>
                    <li className='p-1'>
                        <button onClick={()=>navigate("/chat")} className={loaction.pathname=="/chat"?"btn btn-outline btn-primary":""}>Chat Bot</button>
                    </li>
                    <li className='p-1'>
                        <button onClick={()=>navigate("/info")} className={loaction.pathname=="/info"?"btn btn-outline btn-primary":""}>Information</button>
                    </li>
                    <li className='p-1'>
                        <button onClick={()=>navigate("/faq")} className={loaction.pathname=="/faq"?"btn btn-outline btn-primary":""}>FAQs</button>
                    </li>
                    <li className='p-1'>
                        <button onClick={()=>navigate("/issue")} className={loaction.pathname=="/issue"?"btn btn-outline btn-primary":""}>Error Report</button>
                    </li>
                </ul>
            </div>
            <div className="navbar-end">
                {/* <a className="btn btn-outline btn-primary md:flex hidden">
                Login
                </a> */}
            </div>
        </div>
    );
}

export default NavBar;