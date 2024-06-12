import React from 'react';
import './Navbar.css';
import iconImage from '../../assets/images/icon.png'; 

function Navbar() {
  return (
    <nav className="navbar navbar-custom navbar-expand-lg">
      <div className="container-fluid">
        <a className="navbar-brand" href="#">
            <img src={iconImage} alt="Icon" width="40" className="d-inline-block align-text-top" />
        </a>
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            <li className="nav-item">
              <a className="nav-link active" aria-current="page" href="#">Home</a>
            </li>
          </ul>
          <ul className="navbar-nav ms-auto">
            <li className="nav-item">
              <a className="nav-link" href="/login"><i className="bi bi-box-arrow-in-right"></i> Login</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
