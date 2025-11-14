interface LogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const sizes = {
  sm: 'w-10 h-10',
  md: 'w-12 h-12',
  lg: 'w-16 h-16',
  xl: 'w-24 h-24',
};

export const Logo = ({ size = 'md', className = '' }: LogoProps) => {
  const sizeClass = sizes[size];
  
  return (
    <div className={`${sizeClass} relative ${className}`}>
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <defs>
          {/* Official app color palette - Navy Blue to Bright Teal */}
          <linearGradient id={`gradient-${size}`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style={{ stopColor: '#12436D', stopOpacity: 1 }} />
            <stop offset="100%" style={{ stopColor: '#28A197', stopOpacity: 1 }} />
          </linearGradient>
        </defs>
        
        {/* Rounded square background with gradient */}
        <rect x="8" y="8" width="84" height="84" rx="18" ry="18" fill={`url(#gradient-${size})`}/>
        
        {/* Document/Complaint icon */}
        <g transform="translate(28, 24)">
          {/* Document shape */}
          <path d="M 4 0 L 32 0 L 40 8 L 40 48 L 4 48 L 4 0 Z" fill="white" opacity="0.95"/>
          <path d="M 32 0 L 32 8 L 40 8" fill="none" stroke="white" strokeWidth="2" opacity="0.95"/>
          
          {/* Document lines representing text/complaint */}
          <line x1="10" y1="16" x2="34" y2="16" stroke={`url(#gradient-${size})`} strokeWidth="2.5" strokeLinecap="round"/>
          <line x1="10" y1="24" x2="34" y2="24" stroke={`url(#gradient-${size})`} strokeWidth="2.5" strokeLinecap="round"/>
          <line x1="10" y1="32" x2="26" y2="32" stroke={`url(#gradient-${size})`} strokeWidth="2.5" strokeLinecap="round"/>
          
          {/* Checkmark in circle - representing resolution */}
          <circle cx="22" cy="40" r="6" fill={`url(#gradient-${size})`}/>
          <path d="M 19 40 L 21 42 L 25 38" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </g>
        
        {/* AI/Tech accent - small circuit pattern in corner */}
        <g transform="translate(68, 68)" opacity="0.9">
          <circle cx="6" cy="6" r="2" fill="white"/>
          <circle cx="12" cy="2" r="1.5" fill="white"/>
          <circle cx="2" cy="12" r="1.5" fill="white"/>
          <line x1="6" y1="6" x2="11" y2="3" stroke="white" strokeWidth="1"/>
          <line x1="6" y1="6" x2="3" y2="11" stroke="white" strokeWidth="1"/>
        </g>
      </svg>
    </div>
  );
};
