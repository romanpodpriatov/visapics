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
