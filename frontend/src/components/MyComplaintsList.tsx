import React from 'react';

const MyComplaintsList: React.FC = () => {
  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '48px 24px' }}>
      <h1 style={{ fontSize: '36px', fontWeight: 'bold', color: '#1565C0' }}>
        My Complaints
      </h1>
      <p style={{ fontSize: '16px', color: '#1976D2', marginTop: '16px' }}>
        Coming soon - View and track all your submitted complaints here
      </p>
    </div>
  );
};

export default MyComplaintsList;