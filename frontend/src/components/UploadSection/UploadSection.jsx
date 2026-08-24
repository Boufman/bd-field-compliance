// src/components/UploadSection/UploadSection.jsx

import React from "react";
import UploadBox from "./UploadBox.jsx";

/*
  Apple × Tencent UploadSection Wrapper
  -------------------------------------
  • Soft vertical spacing
  • Locks UploadBox to the centreline
  • Ensures consistent reading rhythm with Results + GraphPreview
  • No external CSS to avoid missing files
*/

const sectionStyle = {
  width: "100%",
  display: "flex",
  justifyContent: "center",
  margin: "0",     // Apple rhythm: 24 → 32 transition spacing
  padding: "0 8px",            // Safe-edge padding for small screens
};

const UploadSection = () => {
  return (
    <section style={sectionStyle}>
      <div style={{ maxWidth: "720px", width: "100%" }}>
        <UploadBox />
      </div>
    </section>
  );
};

export default UploadSection;
