//! The Chinese glyphs the startup pages draw, and nothing more: 16x16 cells
//! of 1-bit rows, two bytes each, MSB first, row-major, over the characters
//! [`CODES`] names in ascending order. `hanzi16.bin` was rasterised from
//! SimSun at 16 px, whose shapes are the crispest small-size bitmaps Windows
//! ships; a wider vocabulary is added by rasterising it into the same table,
//! not by carrying a whole font.
//!
//! Spleen stays the font for the console's log, so everything written to
//! `boot.log` remains ASCII and greppable against the Linux source.

/// A glyph's width, twice Spleen's 8, so it occupies two console cells.
pub const WIDTH: usize = 16;
/// A glyph's height, the same 16 rows Spleen draws.
pub const HEIGHT: usize = 16;
/// One glyph: `HEIGHT` rows of `WIDTH / 8` bytes each.
const BYTES: usize = HEIGHT * (WIDTH / 8);

/// The code points [`CELLS`] holds, ascending for the binary search.
static CODES: &[u32] = &[
    0x4E00, 0x4E0A, 0x4E0B, 0x4E0E, 0x4E8E, 0x4EE5, 0x4F4D, 0x4F7F, 0x4FDD, 0x5148, 0x5165, 0x52A0,
    0x540D, 0x56DE, 0x5B57, 0x5B58, 0x5BC6, 0x62E9, 0x6539, 0x6587, 0x65B0, 0x65E0, 0x660E, 0x6B21,
    0x7528, 0x76D8, 0x7801, 0x79F0, 0x7B26, 0x7EBF, 0x7EDC, 0x7F51, 0x8BF7, 0x8DF3, 0x8F66, 0x8F93,
    0x8FC7, 0x8FD4, 0x9009, 0x9879,
];

/// Every glyph, `BYTES` each, in [`CODES`] order.
static CELLS: &[u8] = include_bytes!("hanzi16.bin");

/// The cell of `code`, or `None` when the table has no such glyph and the
/// caller must draw a replacement instead.
pub fn glyph(code: u32) -> Option<&'static [u8]> {
    let index = CODES.binary_search(&code).ok()?;
    CELLS.get(index * BYTES..(index + 1) * BYTES)
}

/// Whether pixel (`x`, `y`) of `glyph` is set; both are within `WIDTH` and
/// `HEIGHT`.
pub fn pixel(glyph: &[u8], x: usize, y: usize) -> bool {
    glyph[y * (WIDTH / 8) + x / 8] & (0x80 >> (x % 8)) != 0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_named_glyph_has_a_cell_and_an_unnamed_one_does_not() {
        assert_eq!(CELLS.len(), CODES.len() * BYTES);
        for &code in CODES {
            let glyph = glyph(code).expect("a named glyph");
            assert_eq!(glyph.len(), BYTES);
            // A blank cell would be a rasterisation that missed its character.
            assert!(glyph.iter().any(|&row| row != 0), "{code:#06x} is blank");
        }
        assert!(CODES.windows(2).all(|pair| pair[0] < pair[1]), "ascending");
        assert_eq!(glyph(u32::from('A')), None);
        assert_eq!(glyph(0x9F98), None);
    }
}
