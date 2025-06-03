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
        source_urls=["https://travel.state.gov/content/travel/en/passports/need-passport/card.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://travel.state.gov/content/passports/en/passports/photos/photo-composition-template.html"]
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
        source_urls=["https://travel.state.gov/content/travel/en/us-visas.html"]
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
        source_urls=["https://travel.state.gov/content/travel/en/us-visas/diversity-visa.html"]
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
        file_size_max_kb=240,    source_urls=["https://travel.state.gov/content/travel/en/passports/need-passport/card.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.uscis.gov/greencard"]
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
        source_urls=["https://www.auswaertiges-amt.de/en/einreiseundaufenthalt/schengenvisum"],
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
        source_urls=["https://www.gov.uk/browse/abroad/passports"]
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
        background_color="white", glasses_allowed="no",    source_urls=["https://www.gov.uk/browse/abroad/passports"]
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
        background_color="white", glasses_allowed="no",    source_urls=["http://www.uscis.gov/sites/default/files/files/form/i-765instr.pdf", "http://www.uscis.gov/working-united-states/temporary-workers/employment-authorization-certain-h-4-dependent-spouses", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
        background_color="white", glasses_allowed="no",    source_urls=["http://www.nyc.gov/html/nypd/html/permits/handgun_licensing_information.shtml", "http://www.nyc.gov/html/nypd/html/permits/rifle_licensing_information.shtml", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
        background_color="white", glasses_allowed="no",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://travel.state.gov/content/travel/en/us-visas/other-visa-categories/crewmember-visa.html", "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/photos.html"]
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
        background_color="white", glasses_allowed="no",    source_urls=["https://photos.state.gov/libraries/unitedkingdom/164203/dhs/i130-checklist_for_spouse.pdf", "https://jp.usembassy.gov/visas/immigrant-visas/130-petition-checklist/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
        background_color="white", glasses_allowed="no",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
        background_color="white", glasses_allowed="if_no_glare",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
        background_color="white", glasses_allowed="no",    source_urls=["https://www.rn.ca.gov/applicants/lic-exam.shtml", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.rn.ca.gov/applicants/lic-exam.shtmlhttps://www.pcshq.com/?page=NurseExamOnlineAPPInstructions5-17-17.pdf"]
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
        background_color="white", glasses_allowed="no",    source_urls=["https://www.uscis.gov/sites/default/files/document/forms/i-131instr.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
        background_color="white", glasses_allowed="no",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
        background_color="white", glasses_allowed="no",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://travel.state.gov/content/travel/en/passports/need-passport/card.html", "https://www.uscis.gov/greencard"]
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
        background_color="white", glasses_allowed="no",    source_urls=["https://www.uscis.gov/i-131", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
        background_color="white", glasses_allowed="no",    source_urls=["https://travel.state.gov/content/travel/en/passports/need-passport/card.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.uscis.gov/greencard"]
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
        source_urls=["https://travel.state.gov/content/travel/en/passports/need-passport/card.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://travel.state.gov/content/passports/en/passports/photos/photo-composition-template.html"]
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
        background_color="white", glasses_allowed="if_no_glare",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
        background_color="white", glasses_allowed="no",    source_urls=["https://www.atf.gov/file/11281/download", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://photos.state.gov/libraries/unitedkingdom/164203/dhs/i130-checklist_for_spouse.pdf"]
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
        background_color="white", glasses_allowed="no",    source_urls=["https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/photos.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://travel.state.gov/content/travel/en/us-visas/other-visa-categories/crewmember-visa.html", "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/photos.html"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://travel.state.gov/content/travel/en/passports/need-passport/card.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://travel.state.gov/content/passports/en/passports/photos/photo-composition-template.html"]
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
    source_urls=["https://www.uscis.gov/green-card"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.uscis.gov/files/article/M-476.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.uscis.gov/sites/default/files/files/form/i-765instr.pdf", "http://www.uscis.gov/working-united-states/temporary-workers/employment-authorization-certain-h-4-dependent-spouses", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://travel.state.gov/content/travel/en/passports/need-passport/card.html", "https://www.uscis.gov/greencard"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://travel.state.gov/content/travel/en/us-visas/other-visa-categories/crewmember-visa.html", "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/photos.html"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://photos.state.gov/libraries/unitedkingdom/164203/dhs/i130-checklist_for_spouse.pdf", "https://jp.usembassy.gov/visas/immigrant-visas/130-petition-checklist/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.uscis.gov/sites/default/files/document/forms/i-131instr.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.uscis.gov/i-131", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://travel.state.gov/content/travel/en/passports/need-passport/card.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://travel.state.gov/content/passports/en/passports/photos/photo-composition-template.html"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/photos.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.canada.ca/en/immigration-refugees-citizenship/services/new-immigrants/pr-card/apply-renew-replace/photo.html", "https://www.canada.ca/en/department-national-defence/services/benefits-military/transition/service-card.html"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.canada.ca/en/immigration-refugees-citizenship/services/canadian-passports/photos.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.canada.ca/en/department-national-defence/services/benefits-military/transition/service-card.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.canada.ca/en/immigration-refugees-citizenship/services/new-immigrants/pr-card/apply-renew-replace/photo.html"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.norfolk.gov.uk/roads-and-transport/public-transport/buses/concessionary-travel-pass/photo-guidance", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.gov.uk/get-a-child-passport"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.ukba.homeoffice.gov.uk/sitecontent/applicationforms/flr/photoguidance0409.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://photocard.tfl.gov.uk/tfl/showLogon.do?selection=16plus", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.londoncouncils.gov.uk/services/taxicard"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/855728/MSF_4509_Rev_0819_Application_for_a_DB_and-or_BSC.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/900882/Hong_Kong_BNO_English.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://photocard.tfl.gov.uk/tfl/showLogon.do?selection=16plus", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/900882/Hong_Kong_BNO_English.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://malta.mid.ru/ru/grazdanstvo", "https://indonesia.mid.ru/konsulskie-uslugi/grazhdanstvo"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://malta.mid.ru/ru/grazdanstvo", "https://indonesia.mid.ru/konsulskie-uslugi/grazhdanstvo"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://malta.mid.ru/ru/grazdanstvo", "https://indonesia.mid.ru/konsulskie-uslugi/grazhdanstvo"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://malta.mid.ru/ru/grazdanstvo", "https://indonesia.mid.ru/konsulskie-uslugi/grazhdanstvo"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://malta.mid.ru/ru/grazdanstvo", "https://indonesia.mid.ru/konsulskie-uslugi/grazhdanstvo"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://consular.rfembassy.ru/tm/grazhdanstvo_rf/?cid=0&rid=157", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://consular.rfembassy.ru/tm/grazhdanstvo_rf/?cid=0&rid=157", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://consular.rfembassy.ru/tm/grazhdanstvo_rf/?cid=0&rid=157", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://consular.rfembassy.ru/tm/grazhdanstvo_rf/?cid=0&rid=157"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://evisa.kdmid.ru/", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://malta.mid.ru/ru/grazdanstvo"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://evisa.kdmid.ru/", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://visa.kdmid.ru/PetitionChoice.aspx"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://evisa.kdmid.ru/", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://malta.mid.ru/ru/grazdanstvo"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://consular.rfembassy.ru/tm/grazhdanstvo_rf/?cid=0&rid=157", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://malta.mid.ru/ru/grazdanstvo"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://consular.rfembassy.ru/tm/grazhdanstvo_rf/?cid=0&rid=157", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://malta.mid.ru/ru/grazdanstvo"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://consular.rfembassy.ru/tm/grazhdanstvo_rf/?cid=0&rid=157", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://consular.rfembassy.ru/tm/grazhdanstvo_rf/?cid=0&rid=157", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://consular.rfembassy.ru/tm/grazhdanstvo_rf/?cid=0&rid=157", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.passports.gov.au/getting-passport-how-it-works/photo-guidelines", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.qld.gov.au/transport/licensing/proof-of-age#step2"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.immi.gov.au/allforms/pdf/1419.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.qld.gov.au/transport/licensing/proof-of-age#step2"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.qld.gov.au/transport/licensing/proof-of-age#step2", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.qld.gov.au/transport/licensing/proof-of-age#step2", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://immi.homeaffairs.gov.au/form-listing/forms/1195.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.passports.govt.nz/passport-photos/passport-photo-requirements/", "https://www.immigration.govt.nz/new-zealand-visas/apply-for-a-visa/tools-and-information/acceptable-photos"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.immigration.govt.nz/new-zealand-visas/apply-for-a-visa/tools-and-information/acceptable-photos", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.immigration.govt.nz/new-zealand-visas/apply-for-a-visa/tools-and-information/acceptable-photos", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.govt.nz/assets/Documents/Passports-citizenship-and-identity/Application-for-NZ-citizenship-Samoan-adult-and-child.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.passports.govt.nz/assets/Uploads/Forms/COI-RTD-form.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.18plus.org.nz/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.passports.govt.nz/assets/Uploads/Forms/COI-RTD-form.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.18plus.org.nz/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.passports.govt.nz/assets/Uploads/Forms/COI-RTD-form.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.18plus.org.nz/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.immigration.govt.nz/new-zealand-visas/apply-for-a-visa/tools-and-information/acceptable-photos"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.passports.govt.nz/assets/Uploads/Forms/COI-RTD-form.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.18plus.org.nz/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.london.diplo.de/contentblob/3401106/Daten/178573/PhotosIDPassport.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.germany.info/Vertretung/usa/en/05__Legal/02__Directory__Services/01__Visa/__Visa__Photo__Instructions.html", "http://www.germany.info/contentblob/1965686/Daten/178573/Visa_Foto_Mustertafel_L.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.diplomatie.gouv.fr/en/IMG/pdf/sample_photos_france.pdf", "http://www.diplomatie.gouv.fr/en/IMG/pdf/sample_photos_france.pdfhttp://www.consulfrance-losangeles.org/IMG/pdf/Caracteristiques_photos_ENG.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.diplomatie.gouv.fr/en/IMG/pdf/sample_photos_france.pdf", "http://www.diplomatie.gouv.fr/en/IMG/pdf/sample_photos_france.pdfhttp://www.consulfrance-losangeles.org/IMG/pdf/Caracteristiques_photos_ENG.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.cartaidentita.interno.gov.it/modalita-acquisizione-foto/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.cartaidentita.interno.gov.it/modalita-acquisizione-foto/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.ambwashingtondc.esteri.it/Ambasciata_Washington/Menu/In_linea_con_utente/Domande_frequenti/Visti_faq/Visa_Requirements.htm", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.cartaidentita.interno.gov.it/modalita-acquisizione-foto/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.cartaidentita.interno.gov.it/modalita-acquisizione-foto/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.cartaidentita.interno.gov.it/modalita-acquisizione-foto/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.interior.gob.es/web/servicios-al-ciudadano/seguridad/armas-y-explosivos/documentacion-de-la-titularidad-de-armas", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.interior.gob.es/web/servicios-al-ciudadano/dni/documentacion-necesaria-para-su-tramitacion"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.interior.gob.es/web/servicios-al-ciudadano/seguridad/armas-y-explosivos/documentacion-de-la-titularidad-de-armas", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.interior.gob.es/web/servicios-al-ciudadano/dni/documentacion-necesaria-para-su-tramitacion"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.interior.gob.es/web/servicios-al-ciudadano/seguridad/armas-y-explosivos/documentacion-de-la-titularidad-de-armas", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.interior.gob.es/web/servicios-al-ciudadano/dni/documentacion-necesaria-para-su-tramitacion"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.interior.gob.es/web/servicios-al-ciudadano/seguridad/armas-y-explosivos/documentacion-de-la-titularidad-de-armas", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.interior.gob.es/web/servicios-al-ciudadano/dni/documentacion-necesaria-para-su-tramitacion"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.exteriores.gob.es/Consulados/LOSANGELES/es/InformacionParaExtranjeros/Documents/Especificaciones%20foto%20visado.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.interior.gob.es/web/servicios-al-ciudadano/seguridad/armas-y-explosivos/documentacion-de-la-titularidad-de-armas", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.interior.gob.es/web/servicios-al-ciudadano/dni/documentacion-necesaria-para-su-tramitacion"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.gov.pl/web/gov/zdjecie-do-prawa-jazdy", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.paszporty.mswia.gov.pl/portal/content/pdf/plakat_nowe_zdjecia_do_paszportu.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://obywatel.gov.pl/dokumenty-i-dane-osobowe/zdjecie-do-dowodu-lub-paszportu", "https://www.gov.pl/web/gov/zdjecie-do-dowodu-lub-paszportu", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.gov.pl/web/gov/zdjecie-do-prawa-jazdy", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://obywatel.gov.pl/dokumenty-i-dane-osobowe/zdjecie-do-dowodu-lub-paszportu"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.gov.pl/web/gov/zdjecie-do-prawa-jazdy", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://obywatel.gov.pl/dokumenty-i-dane-osobowe/zdjecie-do-dowodu-lub-paszportu"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.gov.pl/web/gov/zdjecie-do-prawa-jazdy", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://obywatel.gov.pl/dokumenty-i-dane-osobowe/zdjecie-do-dowodu-lub-paszportu"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.gov.pl/web/gov/zdjecie-do-prawa-jazdy", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://obywatel.gov.pl/dokumenty-i-dane-osobowe/zdjecie-do-dowodu-lub-paszportu"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.gov.pl/web/gov/zdjecie-do-prawa-jazdy", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://obywatel.gov.pl/dokumenty-i-dane-osobowe/zdjecie-do-dowodu-lub-paszportu"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.government.nl/binaries/government/documenten/publications/2020/06/18/photo-specification-guidelines-2020/RvIG-Fotomatrix-ENG+DEF_20200908.pdf", "https://www.government.nl/binaries/government/documenten/publications/2020/06/18/photo-specification-guidelines-2020/RvIG-Fotomatrix-ENG+DEF_20200908.pdfhttps://www.rvig.nl/sites/default/files/2023-02/Fotomatrix%202020.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://unitedkingdom.nlembassy.org/passports-visas--consular/visas"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://diplomatie.belgium.be/sites/default/files/downloads/eid_fr_0.pdf", "https://diplomatie.belgium.be/fr/Services/services_a_letranger/passeport_belge/passeport_biometrique/belge_en_belgique/qualite_exigee_pour_la_photo", "https://diplomatie.belgium.be/sites/default/files/downloads/2016_matrice_fr.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://diplomatie.belgium.be/sites/default/files/downloads/eid_fr_0.pdf", "https://diplomatie.belgium.be/fr/Services/services_a_letranger/passeport_belge/passeport_biometrique/belge_en_belgique/qualite_exigee_pour_la_photo"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://diplomatie.belgium.be/en/binaries/SchengenEN_tcm312-69379.pdf", "http://countries.diplomatie.belgium.be/en/south_africa/travel_belgium/visa_belgium/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://diplomatie.belgium.be/fr/Services/services_a_letranger/passeport_belge/passeport_biometrique/belge_en_belgique/qualite_exigee_pour_la_photo", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.belgium.be/fr/famille/international/etrangers/documents_de_sejour", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://diplomatie.belgium.be/sites/default/files/downloads/eid_fr_0.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.mzv.cz/manila/en/visa_and_consular_services/visa_information/schengen_visa_stay_of_up_to_90_days/list_of_reguirements_for/tourism.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.mzv.cz/telaviv/en/visa_and_consular_services/passports/index.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.mzv.cz/london/en/visa_and_consular_information/consular_information/czech_passport/index.html"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.mzv.cz/telaviv/en/visa_and_consular_services/passports/index.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.mzv.cz/london/en/visa_and_consular_information/consular_information/czech_passport/index.html"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.swedenabroad.com/en-GB/Embassies/New-Delhi/Visit-Sweden/Visa-for-visiting-Sweden/Tourist-visa/", "http://www.swedenabroad.com/en-GB/Embassies/Kyiv/Visit-Sweden/Visa-for-visiting-Sweden/Schengen-visa-for-visiting-friends--relatives/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.swedenabroad.com/en-GB/Embassies/New-Delhi/Visit-Sweden/Visa-for-visiting-Sweden/Tourist-visa/", "http://www.swedenabroad.com/en-GB/Embassies/Kyiv/Visit-Sweden/Visa-for-visiting-Sweden/Schengen-visa-for-visiting-friends--relatives/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.swedenabroad.com/en-GB/Embassies/New-Delhi/Visit-Sweden/Visa-for-visiting-Sweden/Tourist-visa/", "http://www.swedenabroad.com/en-GB/Embassies/Kyiv/Visit-Sweden/Visa-for-visiting-Sweden/Schengen-visa-for-visiting-friends--relatives/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.bmeia.gv.at/fileadmin/user_upload/Vertretungen/London/Dokumente/Passport_Photographs_Criteria.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.bmeia.gv.at/fileadmin/user_upload/Vertretungen/London/Dokumente/Passport_Photographs_Criteria.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.bmeia.gv.at/fileadmin/user_upload/bmeia/media/Vertretungsbehoerden/Pretoria/Fotokriterien_fuer_Visa.pdf", "http://www.bmeia.gv.at/en/embassy/london/practical-advice/schengen-visa-residence-permits/schengen-visa-application-requirements.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.bmeia.gv.at/fileadmin/user_upload/Vertretungen/London/Dokumente/Passport_Photographs_Criteria.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.bmeia.gv.at/fileadmin/user_upload/Vertretungen/London/Dokumente/Passport_Photographs_Criteria.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.eda.admin.ch/etc/medialib/downloads/edactr/rus.Par.0083.File.tmp/Photograph_Guidelines_en.pdf", "http://www.eda.admin.ch/etc/medialib/downloads/edactr/lka.Par.0024.File.tmp/Guidelines%20for%20Passport%20Photos.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.fedlex.admin.ch/eli/cc/2010/96/de#a12", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.fedlex.admin.ch/eli/cc/2010/96/de#a12", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.sem.admin.ch/dam/data/pass/ausweise/fotomustertafel.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://usa.um.dk/en/travel-and-residence/visa/photo-requirements/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://usa.um.dk/en/travel-and-residence/visa/photo-requirements/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.poliisi.fi/licences/passport/dimensions_and_positioning", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://visa.finland.eu/Saintpeterburg/medical_photospecs.html", "http://www.finland.org.in/public/default.aspx?nodeid=34946&contentlan=2&culture=en-US", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.poliisi.fi/licences/passport/dimensions_and_positioning", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.poliisi.fi/licences/passport/dimensions_and_positioning", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.poliisi.fi/licences/passport/dimensions_and_positioning", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.poliisi.fi/licences/passport/dimensions_and_positioning"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.udi.no/Norwegian-Directorate-of-Immigration/Oversiktsider/Common-pages/Photo-requirements/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.dha.gov.za/index.php/travel-documents2", "http://www.southafrica-canada.ca/Consular/passport-application.htm", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.ebeijing.gov.cn/feature_2/Sino_ltaly_culture_year/Info/Beijing/t921029.htm", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.fmprc.gov.cn/ce/cenp/eng/ConsularService/t1068494.htm"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://ppt.mfa.gov.cn/appo/page/agreement.html", "http://www.fmprc.gov.cn/ce/cenp/eng/ConsularService/t1068494.htm"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://ppt.mfa.gov.cn/appo/page/agreement.html", "http://www.fmprc.gov.cn/ce/cgny/eng/lsyw/lszjx/sbqz/cccbu/t895733.htm"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://ppt.mfa.gov.cn/appo/page/agreement.html", "http://www.fmprc.gov.cn/ce/cgny/eng/lsyw/lszjx/sbqz/cccbu/t895733.htm"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.ebeijing.gov.cn/feature_2/Sino_ltaly_culture_year/Info/Beijing/t921029.htm", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://ppt.mfa.gov.cn/appo/page/agreement.html"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.ebeijing.gov.cn/feature_2/Sino_ltaly_culture_year/Info/Beijing/t921029.htm", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://ppt.mfa.gov.cn/appo/page/agreement.html"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.ebeijing.gov.cn/feature_2/Sino_ltaly_culture_year/Info/Beijing/t921029.htm", "https://www.gov.cn/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.ebeijing.gov.cn/feature_2/Sino_ltaly_culture_year/Info/Beijing/t921029.htm", "https://www.gov.cn/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.ebeijing.gov.cn/feature_2/Sino_ltaly_culture_year/Info/Beijing/t921029.htm", "https://www.gov.cn/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.ebeijing.gov.cn/feature_2/Sino_ltaly_culture_year/Info/Beijing/t921029.htm", "https://www.gov.cn/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://indianvisaonline.gov.in", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://indianvisaonline.gov.in", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://passport.gov.in/oci/welcome", "https://passport.gov.in/oci/Photo-Spec-FINAL.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://passport.gov.in/oci/welcome", "https://passport.gov.in/oci/Photo-Spec-FINAL.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://passport.gov.in/oci/welcome", "https://passport.gov.in/oci/Photo-Spec-FINAL.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://passport.gov.in/oci/welcome", "https://passport.gov.in/oci/Photo-Spec-FINAL.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://passport.gov.in/oci/welcome", "https://passport.gov.in/oci/Photo-Spec-FINAL.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://passport.gov.in/oci/welcome", "https://passport.gov.in/oci/Photo-Spec-FINAL.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://passport.gov.in/oci/welcome", "https://passport.gov.in/oci/Photo-Spec-FINAL.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://indianvisaonline.gov.in", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://aponline.gov.in/Apportal_MessageBoard/DOCUMENTSFORSDPRSDPsUSDPs/pancardprocessdoc.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://indianvisaonline.gov.in", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://embassyofindiabangkok.gov.in/pages.php?id=19"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://indianvisaonline.gov.in", "https://embassyofindiabangkok.gov.in/pages.php?id=19"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://passport.gov.in/oci/welcome", "https://passport.gov.in/oci/Photo-Spec-FINAL.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://passport.gov.in/oci/welcome", "https://passport.gov.in/oci/Photo-Spec-FINAL.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.mofa.go.jp/mofaj/gaiko/apec/btc.html#section4", "https://www.mofa.go.jp/mofaj/files/000149961.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.mofa.go.jp", "https://japanevisa.net/requirements-and-sizes-of-a-japan-visa/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.mofa.go.jp", "https://japanevisa.net/requirements-and-sizes-of-a-japan-visa/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.mofa.go.jp/mofaj/gaiko/apec/btc.html#section4", "https://www.mofa.go.jp/mofaj/files/000149961.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.mofa.go.jp", "https://japanevisa.net/requirements-and-sizes-of-a-japan-visa/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.mofa.go.jp/j_info/visit/visa/index.html", "https://www.mofa.go.jp/files/000124528.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.mofa.go.jp/j_info/visit/visa/index.html", "https://www.mofa.go.jp/files/000124528.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.mofa.go.jp/j_info/visit/visa/index.html", "https://www.mofa.go.jp/files/000124528.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.mofa.go.jp/mofaj/gaiko/apec/btc.html#section4", "https://www.mofa.go.jp/mofaj/files/000149961.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.mofa.go.jp", "https://japanevisa.net/requirements-and-sizes-of-a-japan-visa/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.passport.go.kr/new/issue/photo.php", "http://www.passport.go.kr/img/download/document_1.pdf", "http://www.passport.go.kr/issue/document.php"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.passport.go.kr/new/issue/photo.php", "http://www.passport.go.kr/img/download/document_1.pdf", "http://www.passport.go.kr/issue/document.php"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.immigration.go.kr/HP/IMM80/imm_04/imm_0405/imm_405010.jsp", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.passport.go.kr/new/issue/photo.php"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.immigration.go.kr/HP/IMM80/imm_04/imm_0405/imm_405010.jsp", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.immigration.go.kr/HP/IMM80/imm_04/imm_0405/imm_405010.jsp", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.passport.go.kr/new/issue/photo.php"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.ica.gov.ae", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.dubaivisa.net"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.ica.gov.ae", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.dubaivisa.net"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://smartservices.icp.gov.ae/", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.ica.gov.ae"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://smartservices.icp.gov.ae/", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.ica.gov.ae"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.ica.gov.ae", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://smartservices.icp.gov.ae/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://ica.gov.ae/en/service/issue-family-book/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.gov.il/en/service/new_id", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://embassies.gov.il/stockholm-en/ConsularServices/Pages/Passport-information.aspx", "https://www.gov.il/en/service/new_id", "https://www.gov.il"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://embassies.gov.il/stockholm-en/ConsularServices/Pages/Passport-information.aspx", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.gov.il/en/service/new_id"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://embassies.gov.il/stockholm-en/ConsularServices/Pages/Passport-information.aspx", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://embassies.gov.il/montreal/ConsularServices/Pages/Passports-and-Travel-Documents.aspx"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.israelvisa-india.com/photo.aspx", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.gov.il/en/service/new_id"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.israelvisa-india.com/photo.aspx", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.imi.gov.my/index.php/en/main-services/passport/malaysian-international-passport.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.malaysia.gov.my/media/uploads/fa0d2f5c-e465-41cd-b865-820d79c97dd4.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://educationmalaysia.gov.my/how-to-apply/online-photo-checker.html/", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.malaysia.gov.my/media/uploads/fa0d2f5c-e465-41cd-b865-820d79c97dd4.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.imi.gov.my/index.php/en/main-services/passport/malaysian-international-passport.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.malaysia.gov.my/media/uploads/fa0d2f5c-e465-41cd-b865-820d79c97dd4.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.malaysia.gov.my/media/uploads/fa0d2f5c-e465-41cd-b865-820d79c97dd4.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://malaysiavisa.imi.gov.my/evisa/evisa.jsp"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://www.imi.gov.my/index.php/en/main-services/passport/malaysian-international-passport.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.malaysia.gov.my/media/uploads/fa0d2f5c-e465-41cd-b865-820d79c97dd4.pdf"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://malaysiavisa.imi.gov.my/evisa/evisa.jsp"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.imi.gov.my/index.php/en/main-services/passport/malaysian-international-passport.html", "https://malaysiavisa.imi.gov.my/evisa/evisa.jsp"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://educationmalaysia.gov.my/how-to-apply/online-photo-checker.html/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.lam.gov.my/apec/files/ABTC-Application.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://vfsglobal.com/brazil-evisa/prepare-your-application.html", "http://www.vfsglobal.com/Brazil-eVisa/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://vfsglobal.com/brazil-evisa/prepare-your-application.html", "http://www.vfsglobal.com/Brazil-eVisa/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://mg.gov.br/servico/emissao-da-carteira-de-identidade-1a", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://vfsglobal.com/brazil-evisa/prepare-your-application.html", "http://www.vfsglobal.com/Brazil-eVisa/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://vfsglobal.com/brazil-evisa/prepare-your-application.html", "http://www.vfsglobal.com/Brazil-eVisa/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://ierevan.itamaraty.gov.br/pt-br/passaportes.xml", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://formulario-mre.serpro.gov.br"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://mg.gov.br/servico/emissao-da-carteira-de-identidade-1a", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://apples.ica.gov.sg/apples/index.xhtml", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.ica.gov.sg/common/passport_photo_guidelines", "http://www.ica.gov.sg/page.aspx?pageid=123", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.ica.gov.sg/documents/ic/registration", "https://www.ica.gov.sg/documents/ic/re-registration", "https://www.ica.gov.sg/common/photo-guidelines"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.ica.gov.sg/common/passport_photo_guidelines", "http://www.ica.gov.sg/page.aspx?pageid=123", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.ica.gov.sg/common/passport_photo_guidelines", "http://www.ica.gov.sg/page.aspx?pageid=123", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.mfa.gov.sg/Overseas-Mission/Cairo/Consular-Services/Photocard-Driving-Licence", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.ica.gov.sg/documents/citizencert/replacement"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://marinet.mpa.gov.sg/sdb/dispatch-newapp", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://consulmex.sre.gob.mx/nuevayork/index.php/en/visas-foreigners", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://consulmex.sre.gob.mx/"]
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
    source_urls=["https://consulmex.sre.gob.mx/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://embamex.sre.gob.mx/canada_eng/index.php/consular-fees/5337-permanent-resident-visa-2012", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://consulmex.sre.gob.mx/nuevayork/index.php/en/visas-foreigners"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://consulmex.sre.gob.mx/"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.konsolosluk.gov.tr", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://www.konsolosluk.gov.tr", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["https://randevu.nvi.gov.tr/pages/sss", "https://www.konsolosluk.gov.tr", "https://e-ikamet.goc.gov.tr/Ikamet/IstenenBelgeler/BasvuruFormuBelgelerIliskinAciklamalar"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://cancilleria.gob.ar/visa-para-turismo", "http://cnyor.mrecic.gov.ar/en/node/1817", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://eeeuu.mrecic.gov.ar/es/pasaporte-provisorio-serie", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://cancilleria.gob.ar/visa-para-turismo"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://cnyor.mrecic.gov.ar/en/node/2258", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://cancilleria.gob.ar/visa-para-turismo"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://eeeuu.mrecic.gov.ar/es/pasaporte-provisorio-serie", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://cnyor.mrecic.gov.ar/en/node/2258"]
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
    other_requirements="Auto-generated from visafoto.com data",    source_urls=["http://eeeuu.mrecic.gov.ar/es/pasaporte-provisorio-serie", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://cnyor.mrecic.gov.ar/en/node/2258"]
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
        source_urls=["https://www.passportindia.gov.in/"]
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
        source_urls=["https://www.canada.ca/en/immigration-refugees-citizenship/services/canadian-passports.html"]
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

# Thailand Visa 
# Source: https://visafoto.com/requirements - Thailand visa requirements
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="TH",
        document_name="Visa",
        photo_width_mm=40.0, photo_height_mm=60.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=36.0, eye_max_from_bottom_mm=42.0,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,
        other_requirements="Photo should be taken within 6 months",    source_urls=["https://www.canada.ca/en/immigration-refugees-citizenship/services/canadian-passports.html"]
    )
)

# Thailand Online Visa 
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="TH",
        document_name="Online Visa",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://thaievisa.go.th/static/media/sample-photo.3e754e63.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://www.thaicgny.com/app/download/544568204/visa+form.pdf"]
    )
)

# Philippines Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="PH",
        document_name="Visa",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["http://riyadhpe.dfa.gov.ph/consular-services/visa-services", "http://www.philippineembassy-usa.org/philippines-dc/consular-services-dc/faq-dc/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Philippines Passport
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="PH",
        document_name="Passport",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["http://www.philippine-embassy.de/bln/images/ConsularSection/PassportServices/pdf/info%20bulletin%20on%20the%20implementation%20of%20mrp-22%20dec%2008.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Indonesia Passport
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="ID",
        document_name="Passport",
        photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
        head_min_mm=25.0, head_max_mm=35.0,
        eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,
        other_requirements="Red or white background accepted",    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Indonesia Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="ID",
        document_name="Visa",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://consular.embassyofindonesia.org/visa/genv/TVV/getstarted.html", "http://evisa.kbri-newdelhi.go.id/visa/f/2311e713382d87057619d5cca5fba208"]
    )
)

# Vietnam Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="VN",
        document_name="Visa",
        photo_width_mm=40.0, photo_height_mm=60.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=36.0, eye_max_from_bottom_mm=42.0,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://evisa.xuatnhapcanh.gov.vn/en_US/web/guest/khai-thi-thuc-dien-tu/cap-thi-thuc-dien-tu"]
    )
)

# Vietnam ID Card
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="VN",
        document_name="ID Card",
        photo_width_mm=30.0, photo_height_mm=40.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=24.0, eye_max_from_bottom_mm=28.0,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://evisa.xuatnhapcanh.gov.vn/en_US/web/guest/khai-thi-thuc-dien-tu/cap-thi-thuc-dien-tu", "http://www.moj.gov.vn/vbpq/en/lists/vn%20bn%20php%20lut/view_detail.aspx?itemid=1200"]
    )
)

# Egypt Passport
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="EG",
        document_name="Passport",
        photo_width_mm=40.0, photo_height_mm=60.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=36.0, eye_max_from_bottom_mm=42.0,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://www.egypt.gov.eg/services/listServicesCategory.aspx?ID=350§ion=citizens", "http://www.egyptembassy.net/consular-services/passports-travel/issuing-egyptian-passport/", "http://www.egyptembassy.net/ar/%D8%A7%D8%B3%D8%AA%D8%AE%D8%B1%D8%A7%D8%AC-%D8%AC%D9%88%D8%A7%D8%B2-%D8%B3%D9%81%D8%B1-%D9%85%D8%B5%D8%B1%D9%8A-%D8%AC%D8%AF%D9%8A%D8%AF-%D9%85%D9%85%D9%8A%D9%83%D9%86-%D9%85%D9%82%D8%B1%D9%88%D8%A1/"]
    )
)

# Egypt Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="EG",
        document_name="Visa",
        photo_width_mm=40.0, photo_height_mm=60.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=36.0, eye_max_from_bottom_mm=42.0,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["http://www.egyptembassy.net/consular-services/passports-travel/visa-requirements/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Nigeria Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="NG",
        document_name="Visa",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["http://www.immigration.gov.ng/", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://www.nigerianembassy.ru/index.php/consular-immigration/visa-application.html"]
    )
)

# Nigeria Passport
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="NG",
        document_name="Passport",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://immigration.gov.ng/passport-learn_more", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://portal.immigration.gov.ng/pages/faq"]
    )
)

# Pakistan National ID
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="PK",
        document_name="National ID",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["http://id.nadra.gov.pk/photo-requirements/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Pakistan Passport
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="PK",
        document_name="Passport",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://onlinemrp.dgip.gov.pk/photo-requirements/", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Pakistan Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="PK",
        document_name="Visa",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["http://www.pakconsulatela.org/tourist-visa/", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://visa.nadra.gov.pk/photograph-guide/"]
    )
)

# Bangladesh E-Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="BD",
        document_name="E-Visa",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://www.visa.gov.bd/", "https://apps.apple.com/app/7id-passport-photos/id6447795199", "http://new.bangladeshembassy.ru/images/Forms/Visa_Forms/machine_readable_visa__form.pdf"]
    )
)

# Bangladesh Passport
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="BD",
        document_name="Passport",
        photo_width_mm=40.0, photo_height_mm=50.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=30.0, eye_max_from_bottom_mm=35.0,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["http://www.bangladeshembassy.de/wp-content/uploads/2016/12/NHP-Form.pdf", "http://new.bangladeshembassy.ru/images/Forms/Dual_Nationality_Forms/dual_nationality_application_form.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Iran Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="IR",
        document_name="Visa",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://evisatraveller.mfa.ir/en/request/digital_image_requirement/?title_name=photo", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Iraq Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="IQ",
        document_name="Visa",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["http://www.iraqiembassy.us/page/visas-to-iraq", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Saudi Arabia Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="SA",
        document_name="Visa",
        photo_width_mm=40.0, photo_height_mm=60.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=36.0, eye_max_from_bottom_mm=42.0,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://visa.visitsaudi.com/Home/PhotoSpecifications"]
    )
)

# Morocco Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="MA",
        document_name="Visa",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Morocco Passport
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="MA",
        document_name="Passport",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["http://www.moroccanconsulate.com/pass.cfm", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Algeria Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="DZ",
        document_name="Visa",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Algeria Passport
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="DZ",
        document_name="Passport",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://passeport.interieur.gov.dz/ar/Informations/Normes_Photographie", "https://www.algerian-consulate.org.uk/consulaire/passport/passport-photo-requirements", "http://www.embassyalgeria.ca/passeport"]
    )
)

# Romania Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="RO",
        document_name="Visa",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199", "https://romania-e-visa.com/photo-specifications-and-guidelines-for-romania-visa-application/"]
    )
)

# Romania Passport
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="RO",
        document_name="Passport",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://pasapoarte.mai.gov.ro/indexActe2.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Bulgaria Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="BG",
        document_name="Visa",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["http://www.mfa.bg/en/pages/109/index.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Bulgaria Passport
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="BG",
        document_name="Passport",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["http://www.mfa.bg", "http://www.bulgaria-embassy.org/Consular%20Information/passport/Passport%20Procedures.htm", "http://www.bulgaria-embassy.org/Consular%20Information/passport/pas_samp.pdf"]
    )
)

# Croatia Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="HR",
        document_name="Visa",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["http://za.mfa.hr/?mh=331&mv=2046", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Croatia Passport
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="HR",
        document_name="Passport",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Lithuania Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="LT",
        document_name="Visa",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://uk.mfa.lt/uk/en/travel-and-residence/consular-issues/lithuanian-passport", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Lithuania Passport
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="LT",
        document_name="Passport",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://uk.mfa.lt/uk/en/travel-and-residence/consular-issues/lithuanian-passport", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Latvia Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="LV",
        document_name="Visa",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://www.mfa.gov.lv/en/london/consular-information/documents-required-when-applying-for-a-short-stay-visa-to-enter-latvia", "https://www.mfa.gov.lv/images/KD_faili/Vizas/Mat_RU.pdf", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Latvia Passport
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="LV",
        document_name="Passport",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://www.pmlp.gov.lv/ru/home-ru/uslugi/pasporta/dokumentyi.html", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Estonia Visa
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="EE",
        document_name="Visa",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["http://vm.ee/en/long-stay-d-visa", "https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Estonia Passport
DOCUMENT_SPECIFICATIONS.append(
    PhotoSpecification(
        country_code="EE",
        document_name="Passport",
        photo_width_mm=35.0, photo_height_mm=45.0, dpi=300,
        head_min_percentage=0.65, head_max_percentage=0.75,
        eye_min_from_bottom_mm=27.0, eye_max_from_bottom_mm=33.8,
        background_color="white", glasses_allowed="no",
        neutral_expression_required=True,    source_urls=["https://apps.apple.com/app/7id-passport-photos/id6447795199"]
    )
)

# Check for potential issues if head_min/max_mm and head_min/max_percentage are both None
# for spec_item in DOCUMENT_SPECIFICATIONS:
#     if spec_item.head_min_px is None or spec_item.head_max_px is None:
#         print(f"Warning: Spec {spec_item.country_code} - {spec_item.document_name} has undefined head min/max pixels.")
#     if spec_item.eye_min_from_bottom_px is None or spec_item.eye_max_from_bottom_px is None:
#         if spec_item.eye_min_from_top_px is None or spec_item.eye_max_from_top_px is None :
#             print(f"Warning: Spec {spec_item.country_code} - {spec_item.document_name} has undefined eye line pixels.")
