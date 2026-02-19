# Typhon Bot - Beta Feedback & v0.5 Planning

**Date:** 2026-02-17  
**Testers:** 2 beta users (experienced Alien RPG players)  
**Current Version:** v0.1  
**Overall Reception:** Positive

---

## Beta Tester #1 Feedback

### Positive
- Easy visual character sheet presentation
- Quick-click roll buttons work well
- Clean interface

### Issues & Requests

#### 1. Age Limit Too Restrictive
**Issue:** Character creation restricted to ages 16-60, rejected a 65-year-old character  
**Impact:** Medium — edge case but blocks legitimate character concepts  
**Fix:** Remove or significantly widen age restrictions  
**Priority:** Low (easy fix, affects few users)

#### 2. Skill Training During Creation
**Issue:** Must use `/train` separately for each skill after character creation  
**Impact:** High — tedious for initial setup, breaks flow  
**Fix:** Add skill selection during `/create_character` flow  
**Priority:** High (quality of life improvement)

#### 3. Roll Modifiers Missing
**Issue:** No way to add modifiers for weapons, talents, situational bonuses  
**Suggestion:** `/roll` command with modifier support, or prompt for modifiers on button clicks  
**Impact:** High — affects actual gameplay, players need this for accurate rolls  
**Priority:** High (core mechanics gap)

#### 4. Bane Display Confusing
**Issue:** 1s on base dice shown as banes, but they have no mechanical effect in Alien RPG  
**Impact:** Medium — creates confusion, not mechanically accurate  
**Fix:** Remove bane display/warnings entirely (they're not part of Year Zero Engine)  
**Priority:** Medium (accuracy over flavor)

#### 5. Panic Roll Mechanics Incorrect
**Issue:** Panic triggered but used wrong table, doesn't factor in Resolve  
**Context:** Alien RPG Evolved Edition changed nomenclature:
- 1s on stress dice trigger **Stress Responses** (immediate effects)
- **Panic Rolls** are separate (triggered by other circumstances, use Resolve)
**Impact:** High — core mechanic is wrong  
**Priority:** Critical (game balance affected)

---

## Beta Tester #2 Feedback

### Positive
- Generally positive, lighter feedback

### Issues & Requests

#### 1. Push Button Already Exists
**Status:** ✅ Already implemented — may not have been visible/tested properly

#### 2. Quick Adjustment Buttons on Sheet
**Request:** Add buttons directly to character sheet for:
- Health up/down
- Stress up/down
**Impact:** High — reduces command typing, keeps flow in Discord  
**Priority:** High (excellent UX improvement)

#### 3. Roll Results Summary
**Request:** Show total successes/failures at a glance in roll output  
**Impact:** Medium — readability improvement  
**Priority:** Medium (nice to have)

#### 4. Base Dice Visual Clarity
**Issue:** `Base dice: [4] [2] [3] [3]` format not immediately clear  
**Suggestion:** Better visual differentiation or labeling  
**Impact:** Low — works but could be clearer  
**Priority:** Low (polish)

---

## Summary: Critical vs Nice-to-Have

### Critical Fixes (v0.5 Blockers)
1. **Panic/Stress Response mechanics** — currently broken for Evolved Edition rules
2. **Roll modifiers** — gameplay requirement, not optional
3. **Remove bane warnings** — misleading, not accurate to rules

### High Priority (Major UX)
1. **Skills during character creation** — tedious without this
2. **Quick adjustment buttons** on character sheet (health/stress)

### Medium Priority (Polish)
1. **Widen age restrictions** — easy fix, edge case
2. **Roll results summary** — readability
3. **Better dice visuals** — clarity

### Low Priority (Future)
1. Push button visibility (may already be fine, needs re-test)

---

## Implementation Plan for v0.5

### Phase 1: Rule Corrections (Critical)
- [ ] Remove bane warnings entirely from dice output
- [ ] Implement Stress Response table (replaces current panic on stress dice 1s)
- [ ] Implement proper Panic Roll as separate mechanic (uses Resolve attribute)
- [ ] Add Resolve attribute to character creation

### Phase 2: Roll Modifiers (Critical)
- [ ] Add optional modifier parameter to roll buttons
- [ ] OR implement `/roll` command with dice pool + modifier syntax
- [ ] Display modifier clearly in roll output

### Phase 3: Character Creation UX (High Priority)
- [ ] Add skill selection to `/create_character` flow
- [ ] Multi-step character creation wizard
- [ ] Widen age restrictions (remove or set to 10-100)

### Phase 4: Sheet Interaction (High Priority)
- [ ] Add health +/- buttons to character sheet
- [ ] Add stress +/- buttons to character sheet
- [ ] Auto-refresh sheet after adjustment (remove need for `/sheet`)

### Phase 5: Polish (Medium/Low)
- [ ] Improve roll output formatting
- [ ] Add success/failure summary line
- [ ] Revisit dice visual display

---

## Technical Debt Notes

- Character creation currently single-command — will need refactor for multi-step wizard
- Roll buttons are stateless — adding modifiers requires interaction state management
- Sheet buttons will need dynamic view rebuilding on health/stress changes

---

## Release Target

**v0.5 Goals:**
- Rule-accurate Evolved Edition mechanics
- Streamlined character creation
- Interactive sheet adjustments
- Roll modifier support

**Estimated Scope:** 2-3 development sessions  
**Beta Re-test:** After Phase 2 complete
