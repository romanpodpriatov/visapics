from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple

@dataclass
class PhotoSpecification:
    country_code: str
    document_name: str
    photo_width_mm: float
    photo_height_mm: float
    dpi: int = 300
    head_min_percentage: Optional[float] = None # Min head height as percentage of photo height
    head_max_percentage: Optional[float] = None # Max head height as percentage of photo height
    head_min_mm: Optional[float] = None # Absolute min head height in mm (alternative to percentage)
    head_max_mm: Optional[float] = None # Absolute max head height in mm (alternative to percentage)
    eye_min_from_bottom_mm: Optional[float] = None
    eye_max_from_bottom_mm: Optional[float] = None
    eye_min_from_top_mm: Optional[float] = None # Alternative for some specs
    eye_max_from_top_mm: Optional[float] = None # Alternative for some specs
    distance_top_of_head_to_top_of_photo_min_mm: Optional[float] = None # e.g. Schengen
    distance_top_of_head_to_top_of_photo_max_mm: Optional[float] = None # e.g. Schengen
    background_color: str = "white" # Controlled vocabulary: "white", "off-white", "light_grey", "blue"
    glasses_allowed: str = "no" # Controlled vocabulary: "yes", "no", "if_no_glare"
    neutral_expression_required: bool = True
    other_requirements: Optional[str] = None
    source_url: Optional[str] = None # Optional: URL to the official specification, can be list now
    
    # Enhanced positioning control fields
    head_top_min_dist_from_photo_top_mm: Optional[float] = None
    head_top_max_dist_from_photo_top_mm: Optional[float] = None
    default_head_top_margin_percent: float = 0.12
    min_visual_head_margin_px: int = 5
    min_visual_chin_margin_px: int = 5

    # New fields for visafoto style info
    file_size_min_kb: Optional[int] = None
    file_size_max_kb: Optional[int] = None
    source_urls: Optional[List[str]] = field(default_factory=list)

    MM_PER_INCH = 25.4

    @property
    def photo_width_px(self) -> int:
        return int(self.photo_width_mm / self.MM_PER_INCH * self.dpi)

    @property
    def photo_height_px(self) -> int:
        return int(self.photo_height_mm / self.MM_PER_INCH * self.dpi)

    # Head height in pixels, derived primarily from mm if available, else from percentage
    @property
    def head_min_px(self) -> Optional[int]:
        if self.head_min_mm is not None:
            return int(self.head_min_mm / self.MM_PER_INCH * self.dpi)
        if self.head_min_percentage is not None:
            return int(self.photo_height_px * self.head_min_percentage)
        return None

    @property
    def head_max_px(self) -> Optional[int]:
        if self.head_max_mm is not None:
            return int(self.head_max_mm / self.MM_PER_INCH * self.dpi)
        if self.head_max_percentage is not None:
            return int(self.photo_height_px * self.head_max_percentage)
        return None

    # Eye line from bottom in pixels
    @property
    def eye_min_from_bottom_px(self) -> Optional[int]:
        if self.eye_min_from_bottom_mm is not None:
            return int(self.eye_min_from_bottom_mm / self.MM_PER_INCH * self.dpi)
        return None

    @property
    def eye_max_from_bottom_px(self) -> Optional[int]:
        if self.eye_max_from_bottom_mm is not None:
            return int(self.eye_max_from_bottom_mm / self.MM_PER_INCH * self.dpi)
        return None
        
    # Eye line from top in pixels (useful for direct conversion if spec provides this)
    @property
    def eye_min_from_top_px(self) -> Optional[int]:
        if self.eye_min_from_top_mm is not None:
            return int(self.eye_min_from_top_mm / self.MM_PER_INCH * self.dpi)
        # Alternative: if from_bottom is defined, derive from_top
        elif self.eye_max_from_bottom_px is not None: # eye_max_from_bottom corresponds to eye_min_from_top
             return self.photo_height_px - self.eye_max_from_bottom_px
        return None

    @property
    def eye_max_from_top_px(self) -> Optional[int]:
        if self.eye_max_from_top_mm is not None:
            return int(self.eye_max_from_top_mm / self.MM_PER_INCH * self.dpi)
        # Alternative: if from_bottom is defined, derive from_top
        elif self.eye_min_from_bottom_px is not None: # eye_min_from_bottom corresponds to eye_max_from_top
            return self.photo_height_px - self.eye_min_from_bottom_px
        return None

    # Distance from top of head to top of photo in pixels
    @property
    def distance_top_of_head_to_top_of_photo_min_px(self) -> Optional[int]:
        if self.distance_top_of_head_to_top_of_photo_min_mm is not None:
            return int(self.distance_top_of_head_to_top_of_photo_min_mm / self.MM_PER_INCH * self.dpi)
        return None

    @property
    def distance_top_of_head_to_top_of_photo_max_px(self) -> Optional[int]:
        if self.distance_top_of_head_to_top_of_photo_max_mm is not None:
            return int(self.distance_top_of_head_to_top_of_photo_max_mm / self.MM_PER_INCH * self.dpi)
        return None
    
    # New enhanced positioning control properties  
    @property
    def head_top_min_dist_from_photo_top_px(self) -> Optional[int]:
        if self.head_top_min_dist_from_photo_top_mm is not None:
            return int(self.head_top_min_dist_from_photo_top_mm / self.MM_PER_INCH * self.dpi)
        return None
    
    @property
    def head_top_max_dist_from_photo_top_px(self) -> Optional[int]:
        if self.head_top_max_dist_from_photo_top_mm is not None:
            return int(self.head_top_max_dist_from_photo_top_mm / self.MM_PER_INCH * self.dpi)
        return None

    @property
    def photo_width_inches(self) -> float:
        return self.photo_width_mm / self.MM_PER_INCH

    @property
    def photo_height_inches(self) -> float:
        return self.photo_height_mm / self.MM_PER_INCH

    @property
    def head_min_inches(self) -> Optional[float]:
        if self.head_min_mm is not None:
            return self.head_min_mm / self.MM_PER_INCH
        if self.head_min_percentage is not None:
            return self.photo_height_inches * self.head_min_percentage
        return None

    @property
    def head_max_inches(self) -> Optional[float]:
        if self.head_max_mm is not None:
            return self.head_max_mm / self.MM_PER_INCH
        if self.head_max_percentage is not None:
            return self.photo_height_inches * self.head_max_percentage
        return None

    @property
    def eye_min_from_bottom_inches(self) -> Optional[float]:
        return self.eye_min_from_bottom_mm / self.MM_PER_INCH if self.eye_min_from_bottom_mm is not None else None

    @property
    def eye_max_from_bottom_inches(self) -> Optional[float]:
        return self.eye_max_from_bottom_mm / self.MM_PER_INCH if self.eye_max_from_bottom_mm is not None else None
    
    @property
    def eye_min_from_top_inches(self) -> Optional[float]:
        if self.eye_min_from_top_mm is not None:
            return self.eye_min_from_top_mm / self.MM_PER_INCH
        if self.eye_max_from_bottom_inches is not None:
             return self.photo_height_inches - self.eye_max_from_bottom_inches
        return None

    @property
    def eye_max_from_top_inches(self) -> Optional[float]:
        if self.eye_max_from_top_mm is not None:
            return self.eye_max_from_top_mm / self.MM_PER_INCH
        if self.eye_min_from_bottom_inches is not None:
            return self.photo_height_inches - self.eye_min_from_bottom_inches
        return None
    
    @property
    def required_size_kb_str(self) -> str:
        if self.file_size_min_kb is not None and self.file_size_max_kb is not None:
            return f"From: {self.file_size_min_kb} to: {self.file_size_max_kb} KB"
        elif self.file_size_max_kb is not None:
            return f"Up to: {self.file_size_max_kb} KB"
        return "N/A"


DOCUMENT_SPECIFICATIONS: List[PhotoSpecification] = []

def get_photo_specification(country_code: str, document_name: str) -> Optional[PhotoSpecification]:
    """
    Retrieves a photo specification based on country code and document name.
    """
    for spec in DOCUMENT_SPECIFICATIONS:
        if spec.country_code.lower() == country_code.lower() and \
           spec.document_name.lower() == document_name.lower():
            return spec
    return None

# --- Populate Initial Specifications ---

# US Passport
# Source: https://travel.state.gov/content/travel/en/passports/how-apply/photos.html
# Head height: 1 to 1 3/8 inches (25mm to 35mm)
# Eye height: 1 1/8 to 1 3/8 inches (28mm to 35mm) from bottom of photo (corrected from original prompt's 28.5mm)
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="Passport",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://travel.state.gov/content/travel/en/passports/how-apply/photos.html"]
    )
)

# US Visa (Physical - often same as passport. Digital can vary)
# Source: https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/photos.html
# For digital photos, often 600x600 to 1200x1200 pixels.
# For printed, it refers to passport photo guidelines. We'll use the physical spec here.
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="Visa",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        file_size_max_kb=240, # Typical for digital visa photos
        source_urls=["https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/photos.html",
                     "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/photos/photo-composition-template.html"]
    )
)

# US Visa Lottery (Green Card / Diversity Visa - DV)
# Source: https://travel.state.gov/content/travel/en/us-visas/immigrate/diversity-visa/dv-photo.html
# Digital photo requirements: minimum 600x600 pixels, maximum 1200x1200 pixels
# Square format, JPEG, maximum file size 240KB
# Head height: 50% to 69% of photo height (similar to passport but stricter digital requirements)
# Eye line: between 56% and 69% from bottom of photo
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="Visa Lottery",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_percentage=0.50, head_max_percentage=0.69,
        eye_min_from_bottom_mm=28.4, eye_max_from_bottom_mm=35.1,
        background_color="white", glasses_allowed="no",
        file_size_min_kb=10, file_size_max_kb=240, # Official DV spec
        source_urls=["https://travel.state.gov/content/travel/en/us-visas/immigrate/diversity-visa/dv-photo.html"]
    )
)

# US Green Card (Permanent Resident Card renewal/replacement)
# Similar to DV Lottery requirements but for permanent residents
# Enhanced with head-top positioning requirements for testing
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="Green Card",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_percentage=0.50, head_max_percentage=0.69,
        eye_min_from_bottom_mm=28.4, eye_max_from_bottom_mm=35.1,
        head_top_min_dist_from_photo_top_mm=5.0, head_top_max_dist_from_photo_top_mm=12.0,
        background_color="white", glasses_allowed="no",
        file_size_max_kb=240,
        source_urls=["https://www.uscis.gov/green-card/after-we-grant-your-green-card/replace-green-card"]
    )
)

# Schengen Visa
# Source: Based on typical ICAO standards and common Schengen requirements.
# Often 35x45mm. Head height 32-36mm. Eye line from bottom 29-34mm (Finland example).
# Background: light grey.
# Distance from crown to top of photo: 2-6mm (Finland example uses 3mm as ideal)
# Finland example: https://www.poliisi.fi/files/f/4324/Passikuvaohje_ENG.pdf (Page 10 for diagram)
# Head height: 32-36mm. Eye-to-chin: 15mm. Eye-to-crown: variable.
# Eye line from bottom seems more stable in their diagrams.
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="DE_schengen", # Example for Germany, Schengen generic
        document_name="Visa",
        photo_width_mm=35.0,
        photo_height_mm=45.0,
        dpi=300, # Can be 600 for some applications.
        head_min_mm=32.0,
        head_max_mm=36.0,
        # head_min_percentage=32.0/45.0, # Approx 0.71
        # head_max_percentage=36.0/45.0, # Approx 0.80
        eye_min_from_bottom_mm=29.0, # Based on diagrams like Finnish example
        eye_max_from_bottom_mm=34.0, # Based on diagrams like Finnish example
        distance_top_of_head_to_top_of_photo_min_mm=2.0, # Common range
        distance_top_of_head_to_top_of_photo_max_mm=6.0, # Common range
        background_color="light_grey",
        glasses_allowed="yes", # Generally yes, if no reflections and eyes clearly visible. "no" is safest if unsure.
        neutral_expression_required=True,
        other_requirements="Mouth closed. No shadows on face or background. Good contrast and sharpness.",
        source_url="General ICAO recommendations / specific Schengen country guidelines",
        min_visual_head_margin_px=0  # Allow zero head margin to prioritize eye positioning
    )
)

# Example: UK Passport
# Source: https://www.gov.uk/photos-for-passports
# Photo size: 35x45mm. Digital: min 600x750px.
# Head height (chin to crown): 29mm to 34mm.
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="GB",
        document_name="Passport",
        photo_width_mm=35.0,
        photo_height_mm=45.0,
        dpi=300, # For print. Digital has pixel requirements.
        head_min_mm=29.0,
        head_max_mm=34.0,
        # eye_min_from_bottom_mm: UK spec is less direct on eye line from bottom, focuses on head size and clear space above head.
        # "there must be a gap between your head and the edge of the image"
        # "your face from the bottom of your chin to the crown of your head is between 29mm and 34mm high"
        # For now, we might need to derive eye position or leave it less constrained if not specified.
        # Given head is 29-34mm, and it should be centered with space above, eyes likely similar to Schengen.
        eye_min_from_bottom_mm=25.0, # Placeholder, needs better derivation from UK spec diagram
        eye_max_from_bottom_mm=31.0, # Placeholder
        background_color="light_grey", # or cream
        glasses_allowed="yes", # "if you need to wear them ... no glare"
        neutral_expression_required=True,
        other_requirements="Plain light-coloured background (cream or light grey). No patterns or shadows.",
        source_url="https://www.gov.uk/photos-for-passports"
    )
)

# US Citizenship (Naturalization) - N-400 Application
# Similar to passport requirements
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="Citizenship",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://www.uscis.gov/n-400"]
    )
)

# US Employment Authorization Document (EAD) - I-765
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="Employment Authorization",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://www.uscis.gov/i-765"]
    )
)

# US NY Gun License - 1.5x1.5 inch
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="NY Gun License",
        photo_width_mm=38.1, photo_height_mm=38.1, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.80,
        eye_min_from_bottom_mm=20.0, eye_max_from_bottom_mm=25.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://www.ny.gov/services/apply-pistol-permit"]
    )
)

# US Crew Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="Crew Visa",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://travel.state.gov/content/travel/en/us-visas/"]
    )
)

# US Form I-130 (Petition for Alien Relative)
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="Form I-130",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://www.uscis.gov/i-130"]
    )
)

# US Bar Examination - 300x300 pixels specification
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="Bar Examination",
        photo_width_mm=25.4, photo_height_mm=25.4, dpi=300, # 1x1 inch at 300dpi = 300x300px
        head_min_percentage=0.60, head_max_percentage=0.75,
        eye_min_from_bottom_mm=13.0, eye_max_from_bottom_mm=17.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://www.ncbex.org/"]
    )
)

# US PADI Certification Card - 45x57mm (1.75x2.25 inch)
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="PADI Certification",
        photo_width_mm=45.0, photo_height_mm=57.0, dpi=300,
        head_min_mm=30.0, head_max_mm=40.0,
        eye_min_from_bottom_mm=30.0, eye_max_from_bottom_mm=40.0,
        background_color="white", glasses_allowed="if_no_glare",
        source_urls=["https://www.padi.com/"]
    )
)

# US Nursing License
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="Nursing License",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://www.ncsbn.org/"]
    )
)

# US Re-entry Permit
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="Re-entry Permit",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://www.uscis.gov/i-131"]
    )
)

# US Welding Certificate
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="Welding Certificate",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://www.aws.org/"]
    )
)

# US FOID (Firearm Owner Identification) - 1.25x1.5 inch
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="FOID",
        photo_width_mm=31.75, photo_height_mm=38.1, dpi=300, # 1.25x1.5 inch
        head_min_percentage=0.65, head_max_percentage=0.80,
        eye_min_from_bottom_mm=20.0, eye_max_from_bottom_mm=25.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://www.illinois.gov/ISP/"]
    )
)

# US Advance Parole - I-131
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="Advance Parole",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://www.uscis.gov/i-131"]
    )
)

# US Veteran ID Card
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="Veteran ID Card",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://www.va.gov/records/get-veteran-id-cards/"]
    )
)

# US Passport Card
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="Passport Card",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://travel.state.gov/content/travel/en/passports/how-apply/photos.html"]
    )
)

# US SAT (Standardized Test)
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="SAT",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="if_no_glare",
        source_urls=["https://collegereadiness.collegeboard.org/sat"]
    )
)

# US NFA ATF Form
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="NFA ATF Form",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://www.atf.gov/"]
    )
)

# USCIS (General) - for various USCIS forms
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="US",
        document_name="USCIS",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://www.uscis.gov/"]
    )
)

# Generic Visa Service Providers
# CIBTvisas
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="GENERIC",
        document_name="CIBTvisas",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://cibtvisas.com/"]
    )
)

# VisaCentral
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="GENERIC",
        document_name="VisaCentral",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://www.visacentral.com/"]
    )
)

# Travisa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="GENERIC",
        document_name="Travisa",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://www.travisa.com/"]
    )
)

# VisaHQ
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="GENERIC",
        document_name="VisaHQ",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        source_urls=["https://www.visahq.com/"]
    )
)

# AUTO-GENERATED SPECIFICATIONS FROM VISAFOTO.COM
# This section contains specifications automatically generated from visafoto.com data
# Review and adjust as needed before using in production

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="US",
    document_name="US Visa 2x2 inch (600x600 px, 51x51mm)",
    photo_width_mm=51.0,
    photo_height_mm=51.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.6,
    eye_max_from_bottom_mm=38.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="US",
    document_name="US Passport 2x2 inch (51х51 mm)",
    photo_width_mm=50.8,
    photo_height_mm=50.8,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.5,
    eye_max_from_bottom_mm=38.1,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="US",
    document_name="US Green Card (Permanent Resident) 2x2\"",
    photo_width_mm=50.8,
    photo_height_mm=50.8,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.5,
    eye_max_from_bottom_mm=38.1,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="US",
    document_name="US Citizenship (naturalization) 2x2 inch (51x51 mm)",
    photo_width_mm=51.0,
    photo_height_mm=51.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=30.6,
    eye_max_from_bottom_mm=38.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="US",
    document_name="US Employment Authorization 2x2 inch (51x51 mm)",
    photo_width_mm=51.0,
    photo_height_mm=51.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=30.6,
    eye_max_from_bottom_mm=38.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="US",
    document_name="USA CCHI ID badge 3x3 inch",
    photo_width_mm=76.2,
    photo_height_mm=76.2,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=45.7,
    eye_max_from_bottom_mm=57.1,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="US",
    document_name="USA crew visa 2x2 inch",
    photo_width_mm=50.8,
    photo_height_mm=50.8,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.5,
    eye_max_from_bottom_mm=38.1,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="US",
    document_name="USA Form I-130 2x2 inch",
    photo_width_mm=50.8,
    photo_height_mm=50.8,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.5,
    eye_max_from_bottom_mm=38.1,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="US",
    document_name="USA Re-entry Permit 2x2 inch",
    photo_width_mm=50.8,
    photo_height_mm=50.8,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.5,
    eye_max_from_bottom_mm=38.1,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="US",
    document_name="USA advance parole 2x2 inch",
    photo_width_mm=50.8,
    photo_height_mm=50.8,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.5,
    eye_max_from_bottom_mm=38.1,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="US",
    document_name="US passport card 2x2 inch",
    photo_width_mm=50.8,
    photo_height_mm=50.8,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.5,
    eye_max_from_bottom_mm=38.1,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="US",
    document_name="USCIS 2x2 inch",
    photo_width_mm=50.8,
    photo_height_mm=50.8,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.5,
    eye_max_from_bottom_mm=38.1,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CA",
    document_name="Canada Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CA",
    document_name="Canada Temporary Resident Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CA",
    document_name="Canada Passport 5x7 cm (715x1000 - 2000x2800)",
    photo_width_mm=50.0,
    photo_height_mm=70.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=42.0,
    eye_max_from_bottom_mm=52.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CA",
    document_name="Canada Permanent Resident Card 5x7 cm (715x1000 - 2000x2800)",
    photo_width_mm=50.0,
    photo_height_mm=70.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=42.0,
    eye_max_from_bottom_mm=52.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CA",
    document_name="Canada Citizenship 5x7 cm (50x70mm)",
    photo_width_mm=50.0,
    photo_height_mm=70.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=42.0,
    eye_max_from_bottom_mm=52.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="GB",
    document_name="UK Passport offline 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="GB",
    document_name="UK Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="GB",
    document_name="UK ID / residence card 45x35 mm (4.5x3.5 cm)",
    photo_width_mm=45.0,
    photo_height_mm=35.0,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=21.0,
    eye_max_from_bottom_mm=26.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="GB",
    document_name="British Seaman's discharge book 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="GB",
    document_name="British Seaman's card 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia International Passport Gosuslugi.ru, 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=22.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia International Passport offline, 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=22.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia Internal Passport, 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=22.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia internal Passport for Gosuslugi, 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=22.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia Passport (eyes to bottom of chin 12 mm), 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=22.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia Pensioner ID 3x4",
    photo_width_mm=76.2,
    photo_height_mm=101.6,
    dpi=300,
    head_min_percentage=0.50,
    head_max_percentage=0.85,
    eye_min_from_bottom_mm=20.0,
    eye_max_from_bottom_mm=70.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia Pensioner ID 21x30 for Gosuslugi.ru",
    photo_width_mm=21.0,
    photo_height_mm=30.0,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=20.0,
    eye_max_from_bottom_mm=28.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia Army ID 3x4",
    photo_width_mm=76.2,
    photo_height_mm=101.6,
    dpi=300,
    head_min_percentage=0.50,
    head_max_percentage=0.85,
    eye_min_from_bottom_mm=20.0,
    eye_max_from_bottom_mm=70.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia Work Permit 3x4",
    photo_width_mm=76.2,
    photo_height_mm=101.6,
    dpi=300,
    head_min_percentage=0.50,
    head_max_percentage=0.85,
    eye_min_from_bottom_mm=20.0,
    eye_max_from_bottom_mm=70.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia Student ID 3x4",
    photo_width_mm=76.2,
    photo_height_mm=101.6,
    dpi=300,
    head_min_percentage=0.50,
    head_max_percentage=0.85,
    eye_min_from_bottom_mm=20.0,
    eye_max_from_bottom_mm=70.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia Student ID 25x35 mm (2.5x3.5 cm)",
    photo_width_mm=25.0,
    photo_height_mm=35.0,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=21.0,
    eye_max_from_bottom_mm=26.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=22.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia e-visa 450x600 pixels",
    photo_width_mm=38.1,
    photo_height_mm=50.8,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.85,
    eye_min_from_bottom_mm=22.0,
    eye_max_from_bottom_mm=32.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia visa via VFSGlobal 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=22.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia citizenship 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=22.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia citizenship 3x4 cm",
    photo_width_mm=30.0,
    photo_height_mm=40.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=23.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Moscow social card 3x4 cm",
    photo_width_mm=30.0,
    photo_height_mm=40.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=23.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russian APEC Business Travel Card 4x6 cm",
    photo_width_mm=40.0,
    photo_height_mm=60.0,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=22.0,
    eye_max_from_bottom_mm=38.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia ULM 3x4 cm",
    photo_width_mm=30.0,
    photo_height_mm=40.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=23.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="RU",
    document_name="Russia Seaman’s book 3x4 cm",
    photo_width_mm=30.0,
    photo_height_mm=40.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=23.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AU",
    document_name="Australia Passport 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AU",
    document_name="Australia Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AU",
    document_name="Australia adult proof of age card 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AU",
    document_name="Australia citizenship 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="NZ",
    document_name="New Zealand Passport Online 900x1200 px",
    photo_width_mm=22860.0,
    photo_height_mm=30480.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=18288.0,
    eye_max_from_bottom_mm=22860.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="NZ",
    document_name="New Zealand Visa online 900x1200 px",
    photo_width_mm=22860.0,
    photo_height_mm=30480.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=18288.0,
    eye_max_from_bottom_mm=22860.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="NZ",
    document_name="New Zealand NZETA 540x720 px",
    photo_width_mm=13716.0,
    photo_height_mm=18288.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=10972.8,
    eye_max_from_bottom_mm=13716.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="NZ",
    document_name="New Zealand citizenship 900 x 1200 pixels",
    photo_width_mm=22860.0,
    photo_height_mm=30480.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=18288.0,
    eye_max_from_bottom_mm=22860.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="NZ",
    document_name="New Zealand citizenship 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="NZ",
    document_name="New Zealand Certificate of Identity / Refugee Travel Document 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="NZ",
    document_name="Kiwi Access Card 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="NZ",
    document_name="New Zealand SeaCert 1650x2200 px online",
    photo_width_mm=41910.0,
    photo_height_mm=55880.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=33528.0,
    eye_max_from_bottom_mm=41910.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="NZ",
    document_name="New Zealand SeaCert 35x45 mm offline",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="DE",
    document_name="Germany Passport 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="DE",
    document_name="Germany ID card 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="DE",
    document_name="Germany Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="DE",
    document_name="Germany residence permit 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="DE",
    document_name="Germany Lawyer ID card 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="DE",
    document_name="Germany doctor's identity card 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="FR",
    document_name="France Passport 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="FR",
    document_name="France Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="FR",
    document_name="France ID card 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="FR",
    document_name="Campus France 26x32 mm photo",
    photo_width_mm=26.0,
    photo_height_mm=32.0,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=19.2,
    eye_max_from_bottom_mm=24.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="FR",
    document_name="France Asylum Seeker (Demande D'asile) 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IT",
    document_name="Italy ID card 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IT",
    document_name="Italy Passport 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IT",
    document_name="Italy Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IT",
    document_name="Italy Passport 40x40 mm (LA consulate) 4x4 cm",
    photo_width_mm=40.0,
    photo_height_mm=40.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=23.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IT",
    document_name="Italy fan loyalty card 800x1000 pixels",
    photo_width_mm=20320.0,
    photo_height_mm=25400.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=15240.0,
    eye_max_from_bottom_mm=19050.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IT",
    document_name="Italy fan loyalty card 600x600 pixels",
    photo_width_mm=15240.0,
    photo_height_mm=15240.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=9144.0,
    eye_max_from_bottom_mm=11430.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="ES",
    document_name="Spain passport 3x4 cm",
    photo_width_mm=30.0,
    photo_height_mm=40.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=23.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="ES",
    document_name="Spain DNI (ID card) 32x26 mm",
    photo_width_mm=32.0,
    photo_height_mm=26.0,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=15.6,
    eye_max_from_bottom_mm=19.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="ES",
    document_name="Spain passport 32x26 mm",
    photo_width_mm=32.0,
    photo_height_mm=26.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.85,
    eye_min_from_bottom_mm=15.6,
    eye_max_from_bottom_mm=19.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="ES",
    document_name="Spain TIE card (foreigner ID) 32x26 mm",
    photo_width_mm=32.0,
    photo_height_mm=26.0,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=15.6,
    eye_max_from_bottom_mm=19.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="ES",
    document_name="Spain NIE card 32x26 mm",
    photo_width_mm=32.0,
    photo_height_mm=26.0,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=15.6,
    eye_max_from_bottom_mm=19.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="ES",
    document_name="Spain Passport 40x53 mm",
    photo_width_mm=40.0,
    photo_height_mm=53.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=31.8,
    eye_max_from_bottom_mm=39.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="ES",
    document_name="Spain Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="ES",
    document_name="Spain Visa 2x2 inch (US Chicago consulate)",
    photo_width_mm=50.8,
    photo_height_mm=50.8,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.5,
    eye_max_from_bottom_mm=38.1,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="PL",
    document_name="Poland Passport 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="PL",
    document_name="Poland ID card online 492x633 pixels",
    photo_width_mm=12496.8,
    photo_height_mm=16078.2,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=9646.9,
    eye_max_from_bottom_mm=12058.6,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="PL",
    document_name="Poland ID card 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="PL",
    document_name="Poland ID card online 492x610 pixels",
    photo_width_mm=12496.8,
    photo_height_mm=15494.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=9296.4,
    eye_max_from_bottom_mm=11620.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="PL",
    document_name="Poland Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="PL",
    document_name="Card of the Pole 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="PL",
    document_name="Poland permanent residence card 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="PL",
    document_name="Poland temporary residence card 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="NL",
    document_name="Netherlands Passport 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="NL",
    document_name="Netherlands Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="NL",
    document_name="Dutch ID card 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="BE",
    document_name="Belgium electronic ID card (eID) 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="BE",
    document_name="Belgium Kids-ID 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="BE",
    document_name="Belgium Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="BE",
    document_name="Belgium passport 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="BE",
    document_name="Belgium residence permit 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CZ",
    document_name="Czech Republic Visa 35x45mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CZ",
    document_name="Czechia ID card 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CZ",
    document_name="Czech Republic Passport 35x45mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CZ",
    document_name="Czech Republic Passport 5x5cm (50x50mm)",
    photo_width_mm=50.0,
    photo_height_mm=50.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.0,
    eye_max_from_bottom_mm=37.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CZ",
    document_name="Czechia residence 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="SE",
    document_name="Sweden ID card 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="SE",
    document_name="Sweden Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="SE",
    document_name="Sweden visa 446x580 pixels",
    photo_width_mm=11328.4,
    photo_height_mm=14732.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=8839.2,
    eye_max_from_bottom_mm=11049.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="SE",
    document_name="Sweden passport 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AT",
    document_name="Austrian ID card 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AT",
    document_name="Austria Passport 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AT",
    document_name="Austria Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AT",
    document_name="Austrian residence permit 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AT",
    document_name="Austria Civil engineer ID card 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CH",
    document_name="Switzerland Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CH",
    document_name="Swiss ID card 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CH",
    document_name="Switzerland ID card online 1980x1440px",
    photo_width_mm=50292.0,
    photo_height_mm=36576.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=21945.6,
    eye_max_from_bottom_mm=27432.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CH",
    document_name="Switzerland passport 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="DK",
    document_name="Denmark Visa 35x45mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="DK",
    document_name="Denmark Passport for kk.dk 35x45mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="DK",
    document_name="Denmark Passport 35x45mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="DK",
    document_name="Denmark ID card 35x45mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="DK",
    document_name="University of Copenhagen student card 200x200 pixel",
    photo_width_mm=5080.0,
    photo_height_mm=5080.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=3048.0,
    eye_max_from_bottom_mm=3810.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="DK",
    document_name="Denmark Seafarer's Discharge Book 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="FI",
    document_name="Finland Passport 36x47 mm",
    photo_width_mm=36.0,
    photo_height_mm=47.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=28.2,
    eye_max_from_bottom_mm=35.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="FI",
    document_name="Finland Visa 36x47 mm",
    photo_width_mm=36.0,
    photo_height_mm=47.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=28.2,
    eye_max_from_bottom_mm=35.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="FI",
    document_name="Finland Passport online 500x653 px",
    photo_width_mm=12700.0,
    photo_height_mm=16586.2,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=9951.7,
    eye_max_from_bottom_mm=12439.7,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="FI",
    document_name="Finland ID card online 500x653 px",
    photo_width_mm=12700.0,
    photo_height_mm=16586.2,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=9951.7,
    eye_max_from_bottom_mm=12439.7,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="FI",
    document_name="Finland ID card offline 36x47 mm",
    photo_width_mm=36.0,
    photo_height_mm=47.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=28.2,
    eye_max_from_bottom_mm=35.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="FI",
    document_name="Finland residence 36x47 mm",
    photo_width_mm=36.0,
    photo_height_mm=47.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=28.2,
    eye_max_from_bottom_mm=35.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="NO",
    document_name="Norway Passport 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="NO",
    document_name="Norway Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="ZA",
    document_name="South Africa Passport 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="ZA",
    document_name="South Africa Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CN",
    document_name="China Visa 33x48 mm",
    photo_width_mm=33.0,
    photo_height_mm=48.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=28.8,
    eye_max_from_bottom_mm=36.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CN",
    document_name="China Visa online 354x472 - 420x560 pixels",
    photo_width_mm=8991.6,
    photo_height_mm=11988.8,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=7193.3,
    eye_max_from_bottom_mm=8991.6,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CN",
    document_name="China Passport online 354x472 pixel",
    photo_width_mm=8991.6,
    photo_height_mm=11988.8,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=7193.3,
    eye_max_from_bottom_mm=8991.6,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CN",
    document_name="China Passport online 354x472 pixel old format",
    photo_width_mm=8991.6,
    photo_height_mm=11988.8,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=7193.3,
    eye_max_from_bottom_mm=8991.6,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CN",
    document_name="China Passport 33x48 mm",
    photo_width_mm=33.0,
    photo_height_mm=48.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=28.8,
    eye_max_from_bottom_mm=36.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CN",
    document_name="China Passport 33x48 mm light grey background",
    photo_width_mm=33.0,
    photo_height_mm=48.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=28.8,
    eye_max_from_bottom_mm=36.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CN",
    document_name="China 354x472 pixel with eyes on crosslines",
    photo_width_mm=8991.6,
    photo_height_mm=11988.8,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=7193.3,
    eye_max_from_bottom_mm=8991.6,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CN",
    document_name="China Social Security Card 32x26 mm",
    photo_width_mm=32.0,
    photo_height_mm=26.0,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=15.6,
    eye_max_from_bottom_mm=19.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CN",
    document_name="China Resident ID card 26x32 mm",
    photo_width_mm=26.0,
    photo_height_mm=32.0,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=19.2,
    eye_max_from_bottom_mm=24.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CN",
    document_name="China Medicare card 26x32 mm",
    photo_width_mm=26.0,
    photo_height_mm=32.0,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=19.2,
    eye_max_from_bottom_mm=24.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="CN",
    document_name="China Green Card 33x48 mm",
    photo_width_mm=33.0,
    photo_height_mm=48.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=28.8,
    eye_max_from_bottom_mm=36.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IN",
    document_name="India Visa (2x2 inch, 51x51mm)",
    photo_width_mm=51.0,
    photo_height_mm=51.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.6,
    eye_max_from_bottom_mm=38.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IN",
    document_name="India Visa 190x190 px via VFSglobal.com",
    photo_width_mm=4826.0,
    photo_height_mm=4826.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=2895.6,
    eye_max_from_bottom_mm=3619.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IN",
    document_name="India OCI Passport (2x2 inch, 51x51mm, 200x200 to 1500x1500 pixels)",
    photo_width_mm=51.0,
    photo_height_mm=51.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.6,
    eye_max_from_bottom_mm=38.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IN",
    document_name="India OCI passport 360x360 - 900x900 pixel",
    photo_width_mm=9144.0,
    photo_height_mm=9144.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=5486.4,
    eye_max_from_bottom_mm=6858.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IN",
    document_name="India Passport (2x2 inch, 51x51mm)",
    photo_width_mm=51.0,
    photo_height_mm=51.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.6,
    eye_max_from_bottom_mm=38.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IN",
    document_name="India passport Seva 4.5x3.5 cm",
    photo_width_mm=45.0,
    photo_height_mm=35.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.85,
    eye_min_from_bottom_mm=21.0,
    eye_max_from_bottom_mm=26.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IN",
    document_name="India child passport Seva 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IN",
    document_name="India passport 35x35 mm",
    photo_width_mm=35.0,
    photo_height_mm=35.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.85,
    eye_min_from_bottom_mm=21.0,
    eye_max_from_bottom_mm=26.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IN",
    document_name="India PAN card online 213x213 pixel",
    photo_width_mm=5410.2,
    photo_height_mm=5410.2,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=3246.1,
    eye_max_from_bottom_mm=4057.6,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IN",
    document_name="India PAN card 25x35mm (2.5x3.5cm)",
    photo_width_mm=25.0,
    photo_height_mm=35.0,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=21.0,
    eye_max_from_bottom_mm=26.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IN",
    document_name="India PIO (Person of Indian Origin) 35x35 mm (3.5x3.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=35.0,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=21.0,
    eye_max_from_bottom_mm=26.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IN",
    document_name="India PCC / Birth Certificate 35x35 mm (3.5x3.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=35.0,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=21.0,
    eye_max_from_bottom_mm=26.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IN",
    document_name="India FRRO (Foreigner Registration) 35x35 mm online",
    photo_width_mm=35.0,
    photo_height_mm=35.0,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.85,
    eye_min_from_bottom_mm=21.0,
    eye_max_from_bottom_mm=26.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IN",
    document_name="India Passport for BLS USA Application (2x2 inch, 51x51mm)",
    photo_width_mm=51.0,
    photo_height_mm=51.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.6,
    eye_max_from_bottom_mm=38.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="JP",
    document_name="Japan Residence Card or Certificate of Eligibility 30x40 mm",
    photo_width_mm=30.0,
    photo_height_mm=40.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=23.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="JP",
    document_name="Japan Visa 45x45mm, head 27 mm",
    photo_width_mm=45.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="JP",
    document_name="Japan Visa 2x2 inch (standard visa from the US)",
    photo_width_mm=50.8,
    photo_height_mm=50.8,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.5,
    eye_max_from_bottom_mm=38.1,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="JP",
    document_name="Japan My Number Card 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="JP",
    document_name="Japan Visa 45x45mm, head 34 mm",
    photo_width_mm=45.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="JP",
    document_name="Japan e-visa 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="JP",
    document_name="Japan Passport 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="JP",
    document_name="Japan GoGoNihon 800 pixels 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="JP",
    document_name="Japan APEC Business Travel Card 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="JP",
    document_name="Japan visa 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="KR",
    document_name="South Korea Visa 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="KR",
    document_name="South Korea passport 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="KR",
    document_name="South Korea residence card 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="KR",
    document_name="South Korea Alien Registration 3x4 cm (30x40 mm)",
    photo_width_mm=30.0,
    photo_height_mm=40.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=23.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="KR",
    document_name="South Korea registration card 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AE",
    document_name="UAE Visa online Emirates.com 300x369 pixels",
    photo_width_mm=7620.0,
    photo_height_mm=9372.6,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=5623.6,
    eye_max_from_bottom_mm=7029.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AE",
    document_name="UAE Visa offline 43x55 mm",
    photo_width_mm=43.0,
    photo_height_mm=55.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=33.0,
    eye_max_from_bottom_mm=41.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AE",
    document_name="UAE ID card online 35x45 mm icp.gov.ae",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AE",
    document_name="UAE passport 4x6 cm",
    photo_width_mm=40.0,
    photo_height_mm=60.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=36.0,
    eye_max_from_bottom_mm=45.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AE",
    document_name="UAE ID card 4x6 cm",
    photo_width_mm=40.0,
    photo_height_mm=60.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=36.0,
    eye_max_from_bottom_mm=45.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AE",
    document_name="UAE residence 4x6 cm",
    photo_width_mm=40.0,
    photo_height_mm=60.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=36.0,
    eye_max_from_bottom_mm=45.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AE",
    document_name="UAE family book 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IL",
    document_name="Israel ID card 3.5x4.5 cm (35x45 mm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IL",
    document_name="Israel gov.il 3.5x4.5 cm (35x45 mm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IL",
    document_name="Israel Passport 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IL",
    document_name="Israel Passport 5x5 cm (2x2 in, 51x51 mm)",
    photo_width_mm=51.0,
    photo_height_mm=51.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.6,
    eye_max_from_bottom_mm=38.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IL",
    document_name="Israel Visa 35x45mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="IL",
    document_name="Israel Visa 55x55mm (usually from India)",
    photo_width_mm=55.0,
    photo_height_mm=55.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=33.0,
    eye_max_from_bottom_mm=41.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="MY",
    document_name="Malaysia Passport 35x50 mm white background",
    photo_width_mm=35.0,
    photo_height_mm=50.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.0,
    eye_max_from_bottom_mm=37.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="MY",
    document_name="Malaysia eVisa online application 35x50 mm",
    photo_width_mm=35.0,
    photo_height_mm=50.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.0,
    eye_max_from_bottom_mm=37.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="MY",
    document_name="Malaysia Passport 35x50 mm blue background",
    photo_width_mm=35.0,
    photo_height_mm=50.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.0,
    eye_max_from_bottom_mm=37.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="blue",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="MY",
    document_name="Malaysia Visa 35x50 mm blue background",
    photo_width_mm=35.0,
    photo_height_mm=50.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.0,
    eye_max_from_bottom_mm=37.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="blue",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="MY",
    document_name="Malaysia expat 99x142 pixels blue background",
    photo_width_mm=2514.6,
    photo_height_mm=3606.8,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=2164.1,
    eye_max_from_bottom_mm=2705.1,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="blue",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="MY",
    document_name="Malaysia Visa 35x50 mm white background",
    photo_width_mm=35.0,
    photo_height_mm=50.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.0,
    eye_max_from_bottom_mm=37.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="MY",
    document_name="Malaysia Visa 35x45 mm blue background",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="blue",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="MY",
    document_name="Malaysia Visa 35x45 mm white background",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="MY",
    document_name="Malaysia EMGS 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="MY",
    document_name="Malaysia APEC Business Travel Card 35x50mm (3.5x5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=50.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=30.0,
    eye_max_from_bottom_mm=37.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="BR",
    document_name="Brazil visa online 413x531 px via VFSGlobal",
    photo_width_mm=10490.2,
    photo_height_mm=13487.4,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=8092.4,
    eye_max_from_bottom_mm=10115.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="BR",
    document_name="Brazil visa online 431x531 px",
    photo_width_mm=10947.4,
    photo_height_mm=13487.4,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=8092.4,
    eye_max_from_bottom_mm=10115.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="BR",
    document_name="Brazil ID card 3x4 cm (30x40 mm)",
    photo_width_mm=30.0,
    photo_height_mm=40.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=23.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="BR",
    document_name="Brazil Visa 2x2 inch (from the US) 51x51 mm",
    photo_width_mm=51.0,
    photo_height_mm=51.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=30.6,
    eye_max_from_bottom_mm=38.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="BR",
    document_name="Brazil Passport online 431x531 px",
    photo_width_mm=10947.4,
    photo_height_mm=13487.4,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=8092.4,
    eye_max_from_bottom_mm=10115.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="BR",
    document_name="Brazil Common Passport 5x7 cm",
    photo_width_mm=50.0,
    photo_height_mm=70.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=42.0,
    eye_max_from_bottom_mm=52.5,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="BR",
    document_name="SPTrans Bilhete Único 3x4 cm",
    photo_width_mm=30.0,
    photo_height_mm=40.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=23.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="SG",
    document_name="Singapore visa online 400x514 px",
    photo_width_mm=10160.0,
    photo_height_mm=13055.6,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=7833.4,
    eye_max_from_bottom_mm=9791.7,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="SG",
    document_name="Singapore passport online 400x514 px",
    photo_width_mm=10160.0,
    photo_height_mm=13055.6,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=7833.4,
    eye_max_from_bottom_mm=9791.7,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="SG",
    document_name="Singapore ID card 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="SG",
    document_name="Singapore passport offline 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="SG",
    document_name="Singapore visa offline 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="SG",
    document_name="Singapore Citizenship Certificate 35x45 mm (3.5x4.5 cm)",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="SG",
    document_name="Singapore seaman's discharge book 400x514 px",
    photo_width_mm=10160.0,
    photo_height_mm=13055.6,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=7833.4,
    eye_max_from_bottom_mm=9791.7,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="MX",
    document_name="Mexico passport 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="MX",
    document_name="Mexico visa 35x45 mm",
    photo_width_mm=35.0,
    photo_height_mm=45.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=27.0,
    eye_max_from_bottom_mm=33.8,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="MX",
    document_name="Mexico visa 25x35mm (2.5x3.5cm or 1\"x1.2\")",
    photo_width_mm=25.0,
    photo_height_mm=35.0,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.85,
    eye_min_from_bottom_mm=21.0,
    eye_max_from_bottom_mm=26.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="MX",
    document_name="Mexico permanent residents visa 31x39mm (3.1x3.9cm)",
    photo_width_mm=31.0,
    photo_height_mm=39.0,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.85,
    eye_min_from_bottom_mm=23.4,
    eye_max_from_bottom_mm=29.2,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="MX",
    document_name="Mexico visa 1.5x1.75 inch (1.5 x 1 3/4 inches or 3.8x4.4cm)",
    photo_width_mm=38.0,
    photo_height_mm=44.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=26.4,
    eye_max_from_bottom_mm=33.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="TR",
    document_name="Turkey Visa 50x60 mm (5x6 cm)",
    photo_width_mm=50.0,
    photo_height_mm=60.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=36.0,
    eye_max_from_bottom_mm=45.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="TR",
    document_name="Turkey Passport 50x60 mm (5x6 cm)",
    photo_width_mm=50.0,
    photo_height_mm=60.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=36.0,
    eye_max_from_bottom_mm=45.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="TR",
    document_name="Turkey ID card 5x6 cm",
    photo_width_mm=50.0,
    photo_height_mm=60.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=36.0,
    eye_max_from_bottom_mm=45.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AR",
    document_name="Argentina DNI 4x4 cm (40x40 mm)",
    photo_width_mm=40.0,
    photo_height_mm=40.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.75,
    eye_min_from_bottom_mm=23.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="light_grey",
    glasses_allowed="if_no_glare",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AR",
    document_name="Argentina passport 4x4 cm (40x40 mm)",
    photo_width_mm=40.0,
    photo_height_mm=40.0,
    dpi=300,
    head_min_percentage=0.70,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=23.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AR",
    document_name="Argentina visa 4x4 cm (40x40 mm)",
    photo_width_mm=40.0,
    photo_height_mm=40.0,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.80,
    eye_min_from_bottom_mm=23.0,
    eye_max_from_bottom_mm=30.0,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AR",
    document_name="Argentina passport in USA 1.5x1.5 inch",
    photo_width_mm=38.1,
    photo_height_mm=38.1,
    dpi=300,
    head_min_percentage=0.65,
    head_max_percentage=0.85,
    eye_min_from_bottom_mm=22.9,
    eye_max_from_bottom_mm=28.6,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(
    country_code="AR",
    document_name="Argentina visa in USA 1.5x1.5 inch",
    photo_width_mm=38.1,
    photo_height_mm=38.1,
    dpi=300,
    head_min_percentage=0.60,
    head_max_percentage=0.85,
    eye_min_from_bottom_mm=22.9,
    eye_max_from_bottom_mm=28.6,
    head_top_min_dist_from_photo_top_mm=2.0,
    head_top_max_dist_from_photo_top_mm=8.0,
    background_color="white",
    glasses_allowed="no",
    neutral_expression_required=True,
    other_requirements="Auto-generated from visafoto.com data",
    source_urls=["https://visafoto.com/"]
))

# TODO: Add more specifications as needed.
# - Canada Passport/Visa
# - China Passport/Visa
# - India Passport/Visa/OCI
# - etc.

# India - Passport
# Typical size 2x2 inch (51x51mm). Head size often 65-75% or specific mm.
# Eye position often derived from head centering or top/bottom head margins.
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="IN",
        document_name="Passport",
        photo_width_mm=51.0, 
        photo_height_mm=51.0,
        dpi=300,
        head_min_percentage=0.65, # Approx 33mm on 51mm photo
        head_max_percentage=0.75, # Approx 38mm on 51mm photo
        # If using percentages, mm fields for head can be omitted or calculated for reference.
        # head_min_mm = 51.0 * 0.65, (approx 33.15mm)
        # head_max_mm = 51.0 * 0.75, (approx 38.25mm)
        eye_min_from_bottom_mm=None, # Often, eyes are centered within the head, or head is centered.
        eye_max_from_bottom_mm=None, # This makes direct eye-line-from-bottom spec less common.
        distance_top_of_head_to_top_of_photo_min_mm=3.0, # Common placeholder based on other specs
        distance_top_of_head_to_top_of_photo_max_mm=5.0, # Common placeholder
        background_color="white",
        glasses_allowed="no", # Generally discouraged/not allowed for recent photos
        neutral_expression_required=True,
        other_requirements="Face should be centered. Neutral expression, mouth closed. Both ears visible.",
        source_url="Placeholder - official source verification needed (e.g., Indian Passport Office website)"
    )
)

# Canada - Passport
# Standard size 50mm x 70mm. Head height (chin to crown) 31mm to 36mm.
# Background: Plain white or light-coloured.
# Source: https (colon double slash) www.canada.ca/en/immigration-refugees-citizenship/services/canadian-passports/photos.html
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="CA",
        document_name="Passport",
        photo_width_mm=50.0,
        photo_height_mm=70.0,
        dpi=300, # Official spec might ask for 600 DPI for digital. For print, 300 is common.
        head_min_mm=31.0,
        head_max_mm=36.0,
        # Canadian spec: "The distance from the bottom of the photo to the chin must be minimum 31 mm to maximum 36 mm."
        # This is actually the head height. And "Your face must be square to the camera with a neutral expression, neither frowning nor smiling, and with your mouth closed."
        # "The distance from chin to crown of head must be between 31 mm (1 1/4 inches) and 36 mm (1 7/16 inches)."
        # Eye position: Not directly specified as range from bottom. Usually derived from head centering.
        # Assuming head is centered or positioned with some space from top, and eyes are ~45% from top of head.
        # If head is 31mm, eyes ~14mm from top of head. If head is 36mm, eyes ~16mm from top of head.
        # If top of head is ~3-7mm from top of photo: eye_min_from_top ~17mm, eye_max_from_top ~23mm
        eye_min_from_top_mm=17.0, # Placeholder derived from typical head proportions and top margin
        eye_max_from_top_mm=23.0, # Placeholder
        # Calculate eye position from bottom: photo_height(70mm) - eye_from_top
        eye_min_from_bottom_mm=70.0 - 23.0, # 47.0mm
        eye_max_from_bottom_mm=70.0 - 17.0, # 53.0mm
        background_color="white", # "Plain white or light-coloured background"
        glasses_allowed="no", # Generally no, unless for medical reasons with a signed note.
        neutral_expression_required=True,
        other_requirements="Photos must be taken by a commercial photographer. Stamped or handwritten date on back is required for physical photos.",
        source_url="https://www.canada.ca/en/immigration-refugees-citizenship/services/canadian-passports/photos.html (official site, values interpreted)"
    )
)


# Example of how to use it:
# us_passport_spec = get_photo_specification("US", "Passport")
# if us_passport_spec:
# print(f"US Passport Photo Width in Pixels: {us_passport_spec.photo_width_px}")
# print(f"US Passport Head Min Height in Pixels: {us_passport_spec.head_min_px}")

# schengen_visa_spec = get_photo_specification("DE_schengen", "Visa")
# if schengen_visa_spec:
# print(f"Schengen Visa Eye Min from Bottom (px): {schengen_visa_spec.eye_min_from_bottom_px}")
# print(f"Schengen Visa Head Min (px): {schengen_visa_spec.head_min_px}")
# print(f"Schengen Visa Head Max (px): {schengen_visa_spec.head_max_px}")

# gb_passport_spec = get_photo_specification("GB", "Passport")
# if gb_passport_spec:
# print(f"GB Passport Head Min (px): {gb_passport_spec.head_min_px}")
# print(f"GB Passport Head Max (px): {gb_passport_spec.head_max_px}")

# Check for potential issues if head_min/max_mm and head_min/max_percentage are both None
# for spec_item in DOCUMENT_SPECIFICATIONS:
#     if spec_item.head_min_px is None or spec_item.head_max_px is None:
#         print(f"Warning: Spec {spec_item.country_code} - {spec_item.document_name} has undefined head min/max pixels.")
#     if spec_item.eye_min_from_bottom_px is None or spec_item.eye_max_from_bottom_px is None:
#         if spec_item.eye_min_from_top_px is None or spec_item.eye_max_from_top_px is None :
#             print(f"Warning: Spec {spec_item.country_code} - {spec_item.document_name} has undefined eye line pixels.")
