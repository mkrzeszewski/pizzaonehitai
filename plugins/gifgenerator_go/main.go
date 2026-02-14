package main

import (
	"fmt"
	"image"
	"image/color"
	"image/gif"
	_ "image/jpeg"
	_ "image/png"
	"log"
	"math"
	"math/rand"
	"os"
	"sync"
	"time"

	"golang.org/x/image/draw"

	"github.com/soniakeys/quant/median"
)

var slotImages = []string{
	"assets/img/pizza.png",
	"assets/img/skull.png",
	"assets/img/image1.png",
	"assets/img/image2.png",
	"assets/img/image3.png",
	"assets/img/image4.png",
	"assets/img/image5.png",
}

func createSlotMachineGIF(outputPath string, frames, step int, size image.Point) (string, int, error) {
	slotSize := image.Pt(size.X/3, size.Y/3)
	images := make(map[string]*image.RGBA)
	for _, path := range slotImages {
		img, err := loadAndProcessImage(path, slotSize)
		if err != nil {
			return "", 0, err
		}
		images[path] = img
	}

	reels := make([][]string, 3)
	for i := range reels {
		reel := make([]string, len(slotImages))
		copy(reel, slotImages)
		rand.Shuffle(len(reel), func(i, j int) { reel[i], reel[j] = reel[j], reel[i] })
		reels[i] = reel
	}

	reelOffsets := make([]float64, 3)
	for i := range reelOffsets {
		reelOffsets[i] = rand.Float64() * float64(len(slotImages))
	}

	stopFrames := make([]int, 3)
	for i := range stopFrames {
		stopFrames[i] = frames / 3 * (i + 1)
	}

	baseFrame := image.NewRGBA(image.Rect(0, 0, size.X, size.Y))

	imgH := slotSize.Y
	reelY := (size.Y - 3*imgH) / 2
	positions := []image.Point{
		{0, reelY},
		{slotSize.X, reelY},
		{2 * slotSize.X, reelY},
	}
	middleRect := image.Rect(0, size.Y/3, size.X, 2*size.Y/3)

	var framesList []*image.RGBA
	finalResult := make([]string, 3)

	for frameIdx := 0; frameIdx < frames+60; frameIdx++ {
		currentFrame := image.NewRGBA(baseFrame.Rect)
		copy(currentFrame.Pix, baseFrame.Pix)

		for i := 0; i < 3; i++ {
			offset := math.Mod(reelOffsets[i], 1) * float64(imgH)
			baseIdx := int(reelOffsets[i]) % len(reels[i])

			reelBuffer := image.NewRGBA(image.Rect(0, 0, slotSize.X, 3*imgH))

			for j := 0; j < 4; j++ {
				imgIdx := (baseIdx + j) % len(reels[i])
				imgPath := reels[i][imgIdx]
				img := images[imgPath]

				yPos := j*imgH - int(offset)
				if yPos+imgH <= 0 || yPos >= 3*imgH {
					continue
				}

				yStart := max(yPos, 0)
				yEnd := min(yPos+imgH, 3*imgH)
				srcYStart := yStart - yPos
				// srcYEnd := srcYStart + (yEnd - yStart)

				for y := yStart; y < yEnd; y++ {
					srcY := srcYStart + (y - yStart)
					for x := 0; x < slotSize.X; x++ {
						bufIdx := reelBuffer.PixOffset(x, y)
						bufRgba := reelBuffer.Pix[bufIdx : bufIdx+4]

						imgX := x
						imgY := srcY
						imgIdx := img.PixOffset(imgX, imgY)
						imgRgba := img.Pix[imgIdx : imgIdx+4]

						alpha := imgRgba[3]
						if alpha == 0 {
							continue
						}
						invAlpha := 255 - alpha

						bufR := bufRgba[0]
						bufG := bufRgba[1]
						bufB := bufRgba[2]
						bufA := bufRgba[3]

						imgR := imgRgba[0]
						imgG := imgRgba[1]
						imgB := imgRgba[2]
						imgA := imgRgba[3]

						newR := uint8((uint16(bufR)*uint16(invAlpha) + uint16(imgR)*uint16(alpha)) / 255)
						newG := uint8((uint16(bufG)*uint16(invAlpha) + uint16(imgG)*uint16(alpha)) / 255)
						newB := uint8((uint16(bufB)*uint16(invAlpha) + uint16(imgB)*uint16(alpha)) / 255)
						newA := max_uint8(bufA, imgA)

						bufRgba[0] = newR
						bufRgba[1] = newG
						bufRgba[2] = newB
						bufRgba[3] = newA
					}
				}
			}

			pos := positions[i]
			draw.Draw(currentFrame, image.Rect(pos.X, pos.Y, pos.X+slotSize.X, pos.Y+3*imgH), reelBuffer, image.Point{}, draw.Over)
		}

		drawRect(currentFrame, middleRect, color.RGBA{200, 200, 200, 255}, 5)

		for i := 0; i < 3; i++ {
			if frameIdx <= stopFrames[i] {
				reelOffsets[i] += 0.2
			} else {
				reelOffsets[i] = math.Round(reelOffsets[i])
			}
		}

		if frameIdx == frames+30 {
			for i := 0; i < 3; i++ {
				finalResult[i] = reels[i][(int(reelOffsets[i])+1)%len(reels[i])]
			}
		}

		framesList = append(framesList, currentFrame)
	}

	lastFrame := framesList[len(framesList)-1]
	for i := 0; i < 10; i++ {
		framesList = append(framesList, lastFrame)
	}

	var wg sync.WaitGroup
	palettedFrames := make([]*image.Paletted, len(framesList))
	errors := make(chan error, len(framesList))
	for i, frame := range framesList {
		wg.Add(1)
		go func(idx int, img *image.RGBA) {
			defer wg.Done()
			q := median.Quantizer(128)
			palette := q.Quantize(make(color.Palette, 0, 128), img)
			paletted := image.NewPaletted(img.Bounds(), palette)
			draw.Draw(paletted, img.Bounds(), img, image.Point{}, 1)
			palettedFrames[idx] = paletted
		}(i, frame)
	}

	wg.Wait()
	close(errors)
	if len(errors) > 0 {
		return "", 0, <-errors
	}

	g := &gif.GIF{
		Image:     make([]*image.Paletted, 0, len(palettedFrames)),
		Delay:     make([]int, 0, len(palettedFrames)),
		LoopCount: 0,
	}

	for _, p := range palettedFrames {
		g.Image = append(g.Image, p)
		g.Delay = append(g.Delay, 3)
	}

	file, err := os.Create(outputPath)
	if err != nil {
		return "", 0, err
	}
	defer file.Close()

	if err := gif.EncodeAll(file, g); err != nil {
		return "", 0, err
	}

	resultCount := 1
	var result string
	for _, item := range finalResult {
		count := 0
		for _, other := range finalResult {
			if item == other {
				count++
			}
		}
		if count >= 2 {
			result = item
			resultCount = count
			break
		}
	}

	if result == "" {
		return "", 1, nil
	}
	return result, resultCount, nil
}

func loadAndProcessImage(path string, size image.Point) (*image.RGBA, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	img, _, err := image.Decode(file)
	if err != nil {
		return nil, err
	}

	rgba := image.NewRGBA(img.Bounds())
	draw.Draw(rgba, rgba.Bounds(), img, image.Point{}, draw.Src)

	resized := image.NewRGBA(image.Rect(0, 0, size.X, size.Y))
	draw.ApproxBiLinear.Scale(resized, resized.Rect, rgba, rgba.Bounds(), draw.Src, nil)

	switch img.(type) {
	case *image.NRGBA, *image.RGBA:
	default:
		for i := 3; i < len(resized.Pix); i += 4 {
			resized.Pix[i] = 255
		}
	}

	return resized, nil
}

func drawRect(img *image.RGBA, rect image.Rectangle, c color.RGBA, thickness int) {
	for y := rect.Min.Y; y < rect.Min.Y+thickness; y++ {
		for x := rect.Min.X; x < rect.Max.X; x++ {
			img.Set(x, y, c)
		}
	}
	for y := rect.Max.Y - thickness; y < rect.Max.Y; y++ {
		for x := rect.Min.X; x < rect.Max.X; x++ {
			img.Set(x, y, c)
		}
	}
	for x := rect.Min.X; x < rect.Min.X+thickness; x++ {
		for y := rect.Min.Y; y < rect.Max.Y; y++ {
			img.Set(x, y, c)
		}
	}
	for x := rect.Max.X - thickness; x < rect.Max.X; x++ {
		for y := rect.Min.Y; y < rect.Max.Y; y++ {
			img.Set(x, y, c)
		}
	}
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func max_uint8(a, b uint8) uint8 {
	if a > b {
		return a
	}
	return b
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func main() {
	rand.Seed(time.Now().UnixNano())
	result, count, err := createSlotMachineGIF(string(os.Args[1]), 120, 5, image.Pt(180, 180))
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("{\"result\": \"%s\", \"count\": %d}", result, count)
}
